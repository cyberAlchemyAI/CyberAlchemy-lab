#define _POSIX_C_SOURCE 200809L

#include "Layers/graph/graph.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static const char *PREDICATES[] = {
    "depends_on", "validates", "challenges", "binds", "enforces"
};
static const char *FAMILIES[] = {
    "node_by_id", "outgoing", "incoming", "two_hop",
    "predicate_object", "context_subgraph"
};

typedef struct {
    size_t nodes;
    size_t edges_per_node;
    size_t queries;
    size_t repetitions;
    uint64_t seed;
} config_t;

static uint64_t now_ns(void) {
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return (uint64_t)value.tv_sec * 1000000000ULL + (uint64_t)value.tv_nsec;
}

static int compare_strings(const void *left, const void *right) {
    const char *const *a = left;
    const char *const *b = right;
    return strcmp(*a, *b);
}

static int compare_u64(const void *left, const void *right) {
    uint64_t a = *(const uint64_t *)left;
    uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

static uint64_t percentile(uint64_t *values, size_t count, size_t pct) {
    if (count == 0) return 0;
    qsort(values, count, sizeof(*values), compare_u64);
    size_t index = ((count - 1) * pct + 99) / 100;
    return values[index];
}

static graph_result_t *run_query(graph_layer_t *layer, const config_t *config,
                                 size_t query_index) {
    size_t node = (query_index * 7919ULL + config->seed) % config->nodes;
    char subject[64];
    char object[64];
    snprintf(subject, sizeof(subject), "node:%010zu", node);
    graph_query_t *query = graph_query_create(layer);
    if (!query) return NULL;
    switch (query_index % 6) {
        case 0:
            graph_query_vertex(query, subject);
            break;
        case 1:
            graph_query_vertex(query, subject);
            graph_query_out(query, PREDICATES[query_index % 5]);
            break;
        case 2:
            graph_query_vertex(query, subject);
            graph_query_in(query, PREDICATES[query_index % 5]);
            break;
        case 3:
            graph_query_vertex(query, subject);
            graph_query_out(query, "depends_on");
            graph_query_out(query, "validates");
            break;
        case 4:
            snprintf(object, sizeof(object), "type:%02zu", node % 16);
            graph_query_has(query, "node_type", object);
            break;
        default:
            snprintf(object, sizeof(object), "context:%03zu", node % 128);
            graph_query_has(query, "in_context", object);
            break;
    }
    graph_result_t *result = graph_query_execute_sync(query);
    graph_query_destroy(query);
    return result;
}

static void digest_result(SHA256_CTX *digest, const char *family,
                          graph_result_t *result) {
    SHA256_Update(digest, family, strlen(family));
    const unsigned char zero = 0;
    const unsigned char separator = 0xff;
    SHA256_Update(digest, &zero, 1);
    size_t count = graph_result_count(result);
    const char *const *vertices = graph_result_vertices(result);
    const char **sorted = count ? malloc(count * sizeof(*sorted)) : NULL;
    if (count && !sorted) {
        fprintf(stderr, "allocation failed while digesting result\n");
        exit(7);
    }
    for (size_t index = 0; index < count; ++index) sorted[index] = vertices[index];
    qsort(sorted, count, sizeof(*sorted), compare_strings);
    for (size_t index = 0; index < count; ++index) {
        if (index > 0 && strcmp(sorted[index], sorted[index - 1]) == 0) continue;
        SHA256_Update(digest, sorted[index], strlen(sorted[index]));
        SHA256_Update(digest, &zero, 1);
    }
    SHA256_Update(digest, &separator, 1);
    free(sorted);
}

static int insert_fixture(graph_layer_t *layer, const config_t *config) {
    char subject[64];
    char object[64];
    for (size_t node = 0; node < config->nodes; ++node) {
        snprintf(subject, sizeof(subject), "node:%010zu", node);
        snprintf(object, sizeof(object), "type:%02zu", node % 16);
        if (graph_insert_sync(layer, subject, "node_type", object) != 0) return -1;
        snprintf(object, sizeof(object), "context:%03zu", node % 128);
        if (graph_insert_sync(layer, subject, "in_context", object) != 0) return -1;
        for (size_t edge = 0; edge < config->edges_per_node; ++edge) {
            uint64_t mixed = (uint64_t)node * 1103515245ULL
                           + (uint64_t)edge * 12345ULL + config->seed;
            size_t target = (size_t)(mixed % config->nodes);
            snprintf(object, sizeof(object), "node:%010zu", target);
            if (graph_insert_sync(layer, subject, PREDICATES[edge % 5], object) != 0) return -1;
        }
    }
    return 0;
}

static void print_hex(const unsigned char digest[SHA256_DIGEST_LENGTH]) {
    for (size_t index = 0; index < SHA256_DIGEST_LENGTH; ++index) {
        printf("%02x", digest[index]);
    }
}

int main(int argc, char **argv) {
    config_t config = {1000, 4, 120, 2, 65};
    if (argc == 6) {
        config.nodes = strtoull(argv[1], NULL, 10);
        config.edges_per_node = strtoull(argv[2], NULL, 10);
        config.queries = strtoull(argv[3], NULL, 10);
        config.repetitions = strtoull(argv[4], NULL, 10);
        config.seed = strtoull(argv[5], NULL, 10);
    } else if (argc != 1) {
        fprintf(stderr, "usage: %s [nodes edges_per_node queries repetitions seed]\n", argv[0]);
        return 2;
    }
    if (!config.nodes || !config.edges_per_node || !config.queries || !config.repetitions) {
        fprintf(stderr, "all size parameters must be positive\n");
        return 2;
    }

    uint64_t build_started = now_ns();
    int error_code = 0;
    const char *storage_path = getenv("WAVEDB_BENCH_PATH");
    graph_layer_t *layer = graph_layer_create(storage_path, NULL, NULL, &error_code);
    if (!layer) {
        fprintf(stderr, "graph_layer_create failed: %d\n", error_code);
        return 3;
    }
    char *schema_error = NULL;
    const char *schema =
        "type Node @index(spo, pos) {\n"
        "  node_type: String\n"
        "  in_context: String\n"
        "  depends_on: Node\n"
        "  validates: Node\n"
        "  challenges: Node\n"
        "  binds: Node\n"
        "  enforces: Node\n"
        "}";
    if (graph_schema_parse(layer, schema, &schema_error) != 0) {
        fprintf(stderr, "graph_schema_parse failed: %s\n", schema_error ? schema_error : "unknown");
        free(schema_error);
        graph_layer_destroy(layer);
        return 4;
    }
    free(schema_error);
    if (insert_fixture(layer, &config) != 0) {
        fprintf(stderr, "fixture insertion failed\n");
        graph_layer_destroy(layer);
        return 5;
    }
    uint64_t build_ns = now_ns() - build_started;

    uint64_t insert_started = now_ns();
    if (graph_insert_sync(layer, "node:benchmark:incremental", "binds", "node:0000000000") != 0) {
        fprintf(stderr, "incremental insertion failed\n");
        graph_layer_destroy(layer);
        return 6;
    }
    uint64_t incremental_insert_ns = now_ns() - insert_started;

    SHA256_CTX digest;
    SHA256_Init(&digest);
    for (size_t query_index = 0; query_index < config.queries; ++query_index) {
        graph_result_t *result = run_query(layer, &config, query_index);
        if (!result) {
            fprintf(stderr, "correctness query %zu failed\n", query_index);
            graph_layer_destroy(layer);
            return 8;
        }
        digest_result(&digest, FAMILIES[query_index % 6], result);
        graph_result_destroy(result);
    }
    unsigned char result_digest[SHA256_DIGEST_LENGTH];
    SHA256_Final(result_digest, &digest);

    size_t family_capacity = (config.queries * config.repetitions + 5) / 6;
    uint64_t *samples[6];
    size_t sample_counts[6] = {0};
    for (size_t family = 0; family < 6; ++family) {
        samples[family] = calloc(family_capacity, sizeof(uint64_t));
        if (!samples[family]) return 9;
    }
    for (size_t repetition = 0; repetition < config.repetitions; ++repetition) {
        for (size_t query_index = 0; query_index < config.queries; ++query_index) {
            size_t family = query_index % 6;
            uint64_t started = now_ns();
            graph_result_t *result = run_query(layer, &config, query_index);
            uint64_t elapsed = now_ns() - started;
            if (!result) {
                fprintf(stderr, "timed query %zu failed\n", query_index);
                graph_layer_destroy(layer);
                return 10;
            }
            samples[family][sample_counts[family]++] = elapsed;
            graph_result_destroy(result);
        }
    }

    printf("{\"backend_id\":\"wavedb_graph\",\"benchmark_status\":\"pass\",\"lifecycle_status\":\"%s\",\"lifecycle_blocker\":\"%s\",\"adoption_status\":\"not_evaluable\",\"adoption_blockers\":[\"root_core_license_not_found\",\"rust_integration_not_implemented\"],\"storage_mode\":\"%s\",\"source_commit\":\"9c87530e948e414e077fae4f86262a9439905875\",\"index_policy\":\"spo_pos\",\"node_count\":%zu,\"triple_count\":%zu,\"query_count\":%zu,\"repetitions\":%zu,\"build_ns\":%llu,\"incremental_insert_ns\":%llu,\"interop_result_digest_sha256\":\"",
           storage_path ? "pass" : "fail",
           storage_path ? "" : "WaveDB in-memory initialization and destroy paths attempt WAL or filesystem persistence; graceful destroy is skipped by this isolated benchmark process",
           storage_path ? "persistent" : "in_memory",
           config.nodes, config.nodes * (config.edges_per_node + 2), config.queries,
           config.repetitions, (unsigned long long)build_ns,
           (unsigned long long)incremental_insert_ns);
    print_hex(result_digest);
    printf("\",\"latency_by_query\":{");
    for (size_t family = 0; family < 6; ++family) {
        uint64_t p50 = percentile(samples[family], sample_counts[family], 50);
        uint64_t p95 = percentile(samples[family], sample_counts[family], 95);
        uint64_t p99 = percentile(samples[family], sample_counts[family], 99);
        if (family) printf(",");
        printf("\"%s\":{\"samples\":%zu,\"p50_ns\":%llu,\"p95_ns\":%llu,\"p99_ns\":%llu}",
               FAMILIES[family], sample_counts[family], (unsigned long long)p50,
               (unsigned long long)p95, (unsigned long long)p99);
        free(samples[family]);
    }
    printf("}}\n");
    fflush(stdout);
    if (storage_path) {
        graph_layer_destroy(layer);
    }
    return 0;
}

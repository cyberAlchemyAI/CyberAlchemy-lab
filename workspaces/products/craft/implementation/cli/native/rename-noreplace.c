/* Linux/x64 atomic publication primitive. Only Node-API imports; no libc dependency. */
#if !defined(__linux__) || !defined(__x86_64__) || defined(__ILP32__)
#error This adapter requires Linux x86-64 LP64
#endif
#include <node_api.h>
#include <asm/stat.h>
#include <asm/unistd.h>
#include <linux/fs.h>
#include <errno.h>
#include <limits.h>

_Static_assert(sizeof(long) == 8 && sizeof(struct stat) == 144, "Linux x64 syscall ABI");
_Static_assert(offsetof(struct stat, st_mode) == 24, "Linux x64 mode offset");

static long stat_directory(int fd, struct stat *value) {
  long result;
  __asm__ volatile ("syscall" : "=a"(result)
                    : "a"(__NR_fstat), "D"((long)fd), "S"(value)
                    : "rcx", "r11", "memory");
  return result;
}
static long rename_exclusive(int fd, const char *source, const char *target) {
  long result;
  register long argument4 __asm__("r10") = (long)target;
  register long argument5 __asm__("r8") = RENAME_NOREPLACE;
  __asm__ volatile ("syscall" : "=a"(result)
                    : "a"(__NR_renameat2), "D"((long)fd), "S"(source), "d"((long)fd),
                      "r"(argument4), "r"(argument5)
                    : "rcx", "r11", "memory");
  return result;
}
static napi_value reject(napi_env env, const char *code, const char *message) {
  napi_throw_error(env, code, message);
  return NULL;
}
static int leaf(napi_env env, napi_value value, char output[256]) {
  size_t length = 0;
  if (napi_get_value_string_utf8(env, value, NULL, 0, &length) != napi_ok ||
      length == 0 || length > 255) return 0;
  if (napi_get_value_string_utf8(env, value, output, 256, &length) != napi_ok) return 0;
  for (size_t i = 0; i < length; i++) if (output[i] == '\0' || output[i] == '/') return 0;
  return !(length == 1 && output[0] == '.') && !(length == 2 && output[0] == '.' && output[1] == '.');
}
static const char *error_code(long error) {
  switch (error) {
    case EEXIST: return "EEXIST";
    case ENOTEMPTY: return "ENOTEMPTY";
    case EINVAL: return "EINVAL";
    case EBADF: return "EBADF";
    case ENOTDIR: return "ENOTDIR";
    case ENOENT: return "ENOENT";
    case EACCES: return "EACCES";
    case EPERM: return "EPERM";
    case ENOSYS: return "ENOSYS";
    case EXDEV: return "EXDEV";
    case EOPNOTSUPP: return "EOPNOTSUPP";
    default: return "R09_RENAME_FAILED";
  }
}
static napi_value rename_no_replace(napi_env env, napi_callback_info info) {
  napi_value args[4]; size_t argc = 4; double raw_fd;
  char source[256], target[256]; struct stat parent;
  if (napi_get_cb_info(env, info, &argc, args, NULL, NULL) != napi_ok || argc != 3 ||
      napi_get_value_double(env, args[0], &raw_fd) != napi_ok ||
      !(raw_fd >= 0 && raw_fd <= INT_MAX) || raw_fd != (int)raw_fd ||
      !leaf(env, args[1], source) || !leaf(env, args[2], target))
    return reject(env, "R09_ARGUMENT", "expected a directory descriptor and two nonempty leaf names");
  const int fd = (int)raw_fd;
  long result = stat_directory(fd, &parent);
  if (result < 0) return reject(env, error_code(-result), "cannot inspect parent descriptor");
  /* Linux UAPI file type bits; libc hides S_IF* in strict C11 mode. */
  if ((parent.st_mode & 0170000) != 0040000) return reject(env, "ENOTDIR", "parent descriptor is not a directory");
  result = rename_exclusive(fd, source, target);
  if (result < 0) return reject(env, error_code(-result), "atomic no-replace rename failed");
  napi_value value;
  if (napi_get_undefined(env, &value) != napi_ok) return NULL;
  return value;
}
static napi_value initialize(napi_env env, napi_value exports) {
  napi_property_descriptor property = {"renameNoReplace", NULL, rename_no_replace, NULL, NULL, NULL, napi_default, NULL};
  if (napi_define_properties(env, exports, 1, &property) != napi_ok)
    return reject(env, "R09_NATIVE_API", "cannot register atomic rename adapter");
  return exports;
}
NAPI_MODULE(NODE_GYP_MODULE_NAME, initialize)

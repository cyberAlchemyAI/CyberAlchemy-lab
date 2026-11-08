// Lossless native event transport; child/nested output remains explicitly output.
// Open questions and qualification limits: exhaustive-tests.mjs.
export default async function* events(source) {
  for await (const event of source) {
    yield JSON.stringify(event, (_key, value) => value instanceof Error
      ? {...value, name: value.name, message: value.message, stack: value.stack}
      : typeof value === 'bigint' ? String(value) : value) + '\n';
  }
}

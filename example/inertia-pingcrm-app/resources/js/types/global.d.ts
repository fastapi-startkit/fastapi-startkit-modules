declare global {
  function route(
    name?: string,
    params?: unknown,
    absolute?: boolean
  ): string & { current: (pattern?: string) => boolean };
}

export {};
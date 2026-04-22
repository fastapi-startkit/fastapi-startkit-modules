import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import colors from "picocolors";
import { globSync } from "tinyglobby";
import { createLogger, loadEnv } from "vite";
import fullReload from "vite-plugin-full-reload";
let exitHandlersBound = false;
const refreshPaths = [
  "app**",
  "resources**",
  "routes"
].filter((path2) => fs.existsSync(path2.replace(/\*\*$/, "")));
const logger = createLogger("info", {
  prefix: "[fastapi-vite-plugin]"
});
function fastapi(config) {
  const pluginConfig = resolvePluginConfig(config);
  return [
    resolveFastApiPlugin(pluginConfig),
    ...resolveAssetPlugin(pluginConfig.assets),
    ...resolveFullReloadConfig(pluginConfig)
  ];
}
function resolvePluginConfig(config) {
  if (typeof config === "undefined") {
    throw new Error("fastapi-vite-plugin: missing configuration.");
  }
  if (typeof config === "string" || Array.isArray(config)) {
    config = { input: config, ssr: config };
  }
  if (typeof config.input === "undefined") {
    throw new Error('fastapi-vite-plugin: missing configuration for "input".');
  }
  if (typeof config.publicDirectory === "string") {
    config.publicDirectory = config.publicDirectory.trim().replace(/^\/+/, "");
    if (config.publicDirectory === "") {
      throw new Error("fastapi-vite-plugin: publicDirectory must be a subdirectory. E.g. 'public'.");
    }
  }
  if (typeof config.buildDirectory === "string") {
    config.buildDirectory = config.buildDirectory.trim().replace(/^\/+/, "").replace(/\/+$/, "");
    if (config.buildDirectory === "") {
      throw new Error("fastapi-vite-plugin: buildDirectory must be a subdirectory. E.g. 'build'.");
    }
  }
  if (typeof config.ssrOutputDirectory === "string") {
    config.ssrOutputDirectory = config.ssrOutputDirectory.trim().replace(/^\/+/, "").replace(/\/+$/, "");
  }
  if (config.refresh === true) {
    config.refresh = [{ paths: refreshPaths }];
  }
  return {
    input: config.input,
    publicDirectory: config.publicDirectory ?? "public",
    buildDirectory: config.buildDirectory ?? "build",
    ssr: config.ssr ?? config.input,
    ssrOutputDirectory: config.ssrOutputDirectory ?? "bootstrap/ssr",
    refresh: config.refresh ?? false,
    hotFile: config.hotFile ?? path.join(config.publicDirectory ?? "public", "hot"),
    transformOnServe: config.transformOnServe ?? ((code) => code),
    assets: typeof config.assets === "string" ? [config.assets] : config.assets ?? []
  };
}
function resolveFastApiPlugin(pluginConfig) {
  let viteDevServerUrl;
  let resolvedConfig;
  let userConfig;
  const defaultAliases = {
    "@": "/resources/js"
  };
  return {
    name: "fastapi-vite-plugin",
    enforce: "post",
    config: (config, { command, mode }) => {
      userConfig = config;
      const ssr = !!userConfig.build?.ssr;
      const env = loadEnv(mode, userConfig.envDir || process.cwd(), "");
      const assetUrl = env.ASSET_URL ?? "";
      return {
        base: userConfig.base ?? (command === "build" ? resolveBase(pluginConfig, assetUrl) : ""),
        publicDir: userConfig.publicDir ?? false,
        build: {
          manifest: userConfig.build?.manifest ?? (ssr ? false : "manifest.json"),
          ssrManifest: userConfig.build?.ssrManifest ?? (ssr ? "ssr-manifest.json" : false),
          outDir: userConfig.build?.outDir ?? resolveOutDir(pluginConfig, ssr),
          rolldownOptions: {
            input: userConfig.build?.rolldownOptions?.input ?? userConfig.build?.rollupOptions?.input ?? resolveInput(pluginConfig, ssr)
          },
          assetsInlineLimit: userConfig.build?.assetsInlineLimit ?? 0
        },
        server: {
          origin: userConfig.server?.origin ?? "http://localhost:5173",
          cors: userConfig.server?.cors ?? true
        },
        resolve: {
          alias: Array.isArray(userConfig.resolve?.alias) ? [
            ...userConfig.resolve?.alias ?? [],
            ...Object.keys(defaultAliases).map((alias) => ({
              find: alias,
              replacement: defaultAliases[alias]
            }))
          ] : {
            ...defaultAliases,
            ...userConfig.resolve?.alias
          }
        }
      };
    },
    configResolved(config) {
      resolvedConfig = config;
    },
    transform(code) {
      if (resolvedConfig.command === "serve") {
        code = code.replace(/http:\/\/localhost:5173/g, viteDevServerUrl);
        return pluginConfig.transformOnServe(code, viteDevServerUrl);
      }
    },
    configureServer(server) {
      const envDir = resolvedConfig.envDir || process.cwd();
      const appUrl = loadEnv(resolvedConfig.mode, envDir, "APP_URL").APP_URL ?? "undefined";
      server.httpServer?.once("listening", () => {
        const address = server.httpServer?.address();
        const isAddressInfo = (x) => typeof x === "object";
        if (isAddressInfo(address)) {
          viteDevServerUrl = userConfig.server?.origin ? userConfig.server.origin : resolveDevServerUrl(address, server.config, userConfig);
          const hotFileParentDirectory = path.dirname(pluginConfig.hotFile);
          if (!fs.existsSync(hotFileParentDirectory)) {
            fs.mkdirSync(hotFileParentDirectory, { recursive: true });
            setTimeout(() => {
              logger.info(`Hot file directory created ${colors.dim(fs.realpathSync(hotFileParentDirectory))}`, { clear: true, timestamp: true });
            }, 200);
          }
          fs.writeFileSync(pluginConfig.hotFile, `${viteDevServerUrl}${server.config.base.replace(/\/$/, "")}`);
          setTimeout(() => {
            server.config.logger.info(`
  ${colors.red(`${colors.bold("FASTAPI")}`)}  ${colors.dim("plugin")} ${colors.bold(`v${pluginVersion()}`)}`);
            server.config.logger.info("");
            server.config.logger.info(`  ${colors.green("\u279C")}  ${colors.bold("APP_URL")}: ${colors.cyan(appUrl.replace(/:(\d+)/, (_, port) => `:${colors.bold(port)}`))}`);
          }, 100);
        }
      });
      if (!exitHandlersBound) {
        const clean = () => {
          if (fs.existsSync(pluginConfig.hotFile)) {
            fs.rmSync(pluginConfig.hotFile);
          }
        };
        process.on("exit", clean);
        process.on("SIGINT", () => process.exit());
        process.on("SIGTERM", () => process.exit());
        process.on("SIGHUP", () => process.exit());
        exitHandlersBound = true;
      }
      return () => server.middlewares.use((req, res, next) => {
        if (req.url === "/index.html") {
          res.statusCode = 404;
          res.end(
            fs.readFileSync(path.join(dirname(), "dev-server-index.html")).toString().replace(/{{ APP_URL }}/g, appUrl)
          );
        }
        next();
      });
    }
  };
}
function pluginVersion() {
  try {
    return JSON.parse(fs.readFileSync(path.join(dirname(), "../package.json")).toString())?.version;
  } catch {
    return "unknown";
  }
}
function resolveBase(config, assetUrl) {
  return assetUrl + (!assetUrl.endsWith("/") ? "/" : "") + config.buildDirectory + "/";
}
function resolveInput(config, ssr) {
  if (ssr) {
    return config.ssr;
  }
  return config.input;
}
function resolveOutDir(config, ssr) {
  if (ssr) {
    return config.ssrOutputDirectory;
  }
  return path.join(config.publicDirectory, config.buildDirectory);
}
function resolveAssetPlugin(assets) {
  if (assets.length === 0) {
    return [];
  }
  return [{
    name: "fastapi:assets",
    apply: "build",
    buildStart() {
      for (const file of globSync(assets)) {
        if (fs.statSync(file).isFile()) {
          this.emitFile({ type: "asset", name: path.basename(file), originalFileName: file, source: fs.readFileSync(file) });
        }
      }
    }
  }];
}
function resolveFullReloadConfig({ refresh: config }) {
  if (typeof config === "boolean") {
    return [];
  }
  if (typeof config === "string") {
    config = [{ paths: [config] }];
  }
  if (!Array.isArray(config)) {
    config = [config];
  }
  if (config.some((c) => typeof c === "string")) {
    config = [{ paths: config }];
  }
  return config.flatMap((c) => {
    const plugin = fullReload(c.paths, c.config);
    plugin.__fastapi_plugin_config = c;
    return plugin;
  });
}
function resolveDevServerUrl(address, config, userConfig) {
  const configHmrProtocol = typeof config.server.hmr === "object" ? config.server.hmr.protocol : null;
  const clientProtocol = configHmrProtocol ? configHmrProtocol === "wss" ? "https" : "http" : null;
  const serverProtocol = config.server.https ? "https" : "http";
  const protocol = clientProtocol ?? serverProtocol;
  const configHmrHost = typeof config.server.hmr === "object" ? config.server.hmr.host : null;
  const configHost = typeof config.server.host === "string" ? config.server.host : null;
  const serverAddress = isIpv6(address) ? `[${address.address}]` : address.address;
  const host = configHmrHost ?? configHost ?? serverAddress;
  const configHmrClientPort = typeof config.server.hmr === "object" ? config.server.hmr.clientPort : null;
  const port = configHmrClientPort ?? address.port;
  return `${protocol}://${host}:${port}`;
}
function isIpv6(address) {
  return address.family === "IPv6" || address.family === 6;
}
function dirname() {
  return fileURLToPath(new URL(".", import.meta.url));
}
export {
  fastapi as default,
  refreshPaths
};

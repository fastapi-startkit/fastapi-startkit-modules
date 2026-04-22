import { ConfigEnv, Plugin, Rolldown, UserConfig } from "vite";
import { Config as FullReloadConfig } from "vite-plugin-full-reload";
interface RefreshConfig {
    paths: string[];
    config?: FullReloadConfig;
}
interface PluginConfig {
    input: Rolldown.InputOption;
    publicDirectory?: string;
    buildDirectory?: string;
    hotFile?: string;
    ssr?: Rolldown.InputOption;
    ssrOutputDirectory?: string;
    refresh?: boolean | string | string[] | RefreshConfig | RefreshConfig[];
    transformOnServe?: (code: string, url: DevServerUrl) => string;
    /**
     * Asset file glob patterns to include in the build.
     *
     * Files matching these patterns will be processed and versioned by Vite,
     * even if they are not imported in your JavaScript. This is useful for
     * assets referenced in templates via `Vite::asset()`.
     *
     * @default []
     */
    assets?: string | string[];
}
type DevServerUrl = `${"http" | "https"}://${string}:${number}`;
interface FastApiPlugin extends Plugin {
    config: (config: UserConfig, env: ConfigEnv) => UserConfig;
}
export declare const refreshPaths: string[];
export default function fastapi(config: string | string[] | PluginConfig): [FastApiPlugin, ...Plugin[]];
export {};

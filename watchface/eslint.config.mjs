import js from "@eslint/js";
import stylistic from "@stylistic/eslint-plugin";

// Shared globals provided by the JS runtimes the watchface runs in.
// Extend these as the code grows (e.g. Timer, trace, Resource on the watch
// side; XMLHttpRequest, localStorage on the phone side).
const embeddedJsGlobals = {
  screen: "readonly",
  watch: "readonly",
  console: "readonly",
  Timer: "readonly",
  trace: "readonly",
};

const pkjsGlobals = {
  Pebble: "readonly",
  console: "readonly",
  XMLHttpRequest: "readonly",
  localStorage: "readonly",
  navigator: "readonly",
};

export default [
  // eslint.config.mjs itself is tooling, not watch source — keep it out of the
  // source style rules (4-space, no trailing comma) it would otherwise violate.
  { ignores: ["build/", "node_modules/", "eslint.config.mjs"] },

  // Correctness rules (no-undef, no-unused-vars, ...) for all JS.
  js.configs.recommended,

  // Consistent styling without a separate formatter. Tuned to the existing
  // code conventions (4-space indent, double quotes, semicolons) rather than
  // the opinionated defaults, so linting enforces consistency instead of a
  // wholesale restyle.
  stylistic.configs.customize({
    indent: 4,
    quotes: "double",
    semi: true,
    commaDangle: "never",
  }),

  // On-watch code: Moddable XS, ES modules.
  {
    files: ["src/embeddedjs/**/*.js"],
    languageOptions: {
      sourceType: "module",
      globals: embeddedJsGlobals,
    },
  },

  // Phone-side PebbleKit JS: classic script scope.
  {
    files: ["src/pkjs/**/*.js"],
    languageOptions: {
      sourceType: "script",
      globals: pkjsGlobals,
    },
  },
];

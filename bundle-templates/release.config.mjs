export default {
  branches: [{ name: "main" }],
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      {
        changelogFile: "CHANGELOG.md",
      },
    ],
    [
      "@semantic-release/exec",
      {
        prepareCmd: "sed -i 's/version `[0-9]\\+\\.[0-9]\\+\\.[0-9]\\+`/version `${nextRelease.version}`/g' template/{{.domain_name}}/README.md.tmpl template/{{.domain_name}}/docs/README.md.tmpl || true",
      },
    ],
    [
      "@semantic-release/git",
      {
        assets: [
          "CHANGELOG.md",
          "template/{{.domain_name}}/README.md.tmpl",
          "template/{{.domain_name}}/docs/index.md.tmpl",
        ],
        message: "chore(release): ${nextRelease.version} [skip ci]",
      },
    ],
    "@semantic-release/github",
  ],
};

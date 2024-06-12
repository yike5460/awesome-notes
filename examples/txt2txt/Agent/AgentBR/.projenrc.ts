import { awscdk } from 'projen';
const project = new awscdk.AwsCdkTypeScriptApp({
  authorName: 'yike5460',
  cdkVersion: '2.1.0',
  defaultReleaseBranch: 'main',
  name: 'Agent',
  projenrcTs: true,
  renovatebot: true,
  stale: true,

  // deps: [],                /* Runtime dependencies of this module. */
  // description: undefined,  /* The description is just a string that helps people understand the purpose of the package. */
  // devDeps: [],             /* Build dependencies for this module. */
  // packageName: undefined,  /* The "name" in package.json. */
});
project.synth();
import { awscdk } from 'projen';
import { NpmAccess } from 'projen/lib/javascript';

const project = new awscdk.AwsCdkConstructLibrary({
  author: 'yike5460',
  authorAddress: 'yike5460@163.com',
  cdkVersion: '2.149.0',
  defaultReleaseBranch: 'main',
  // deps: ['[aws-cdk-lib,constructs]'],
  jsiiVersion: '~5.4.0',
  name: 'intelli-agent',
  projenrcTs: true,
  repositoryUrl: 'https://github.com/yike5460/justNotes.git',

  // cdkDependencies is not used for CDK 2.x. Use "peerDeps" or "deps" instead
  // cdkDependencies: ['aws-cdk-lib'],
  bundledDeps: ['aws-sdk'], // If you need AWS SDK in your Lambda

  // Publish to npm
  npmAccess: NpmAccess.PUBLIC,

  // Include Lambda assets
  publishToPypi: {
    distName: 'intelli-agent',
    module: 'intelli_agent',
  },

  // description: undefined,  /* The description is just a string that helps people understand the purpose of the package. */
  // devDeps: [],             /* Build dependencies for this module. */
  // packageName: undefined,  /* The "name" in package.json. */
});

// Include Lambda asset in the package
project.addPackageIgnore('!/lambda');
project.synth();
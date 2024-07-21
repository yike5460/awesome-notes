# Build a Constructor for Generative AI

## Start from scratch
1. Initialize your project using projen
```bash
npx projen new awscdk-construct --name intelli-agent
```

2. Add your construct implementation ts file (intell-agent-construct e.g.) inside src folder and corresponding lambda function code (e.g. lambda folder) in root folder

3. Import your custom construct in the main stack file (index.ts)
```typescript
export * from './intelli-agent-construct';
```

4. Adjust your test file (intell-agent.test.ts) inside test folder and run the test
```bash
npx projen test

 PASS  test/intelli-agent.test.ts
  ✓ Intelli Agent Construct (437 ms)

----------------------------|---------|----------|---------|---------|-------------------
File                        | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s 
----------------------------|---------|----------|---------|---------|-------------------
All files                   |     100 |      100 |     100 |     100 |                   
 intelli-agent-construct.ts |     100 |      100 |     100 |     100 |                   
----------------------------|---------|----------|---------|---------|-------------------
Test Suites: 1 passed, 1 total
Tests:       1 passed, 1 total
Snapshots:   0 total
Time:        3.648 s, estimated 4 s
```
5. Update the .projenrc.ts file to include the new Lambda asset and run npx projen to update the project configuration
```bash
npx projen
```

6. Build your project
```bash
npx projen build
```

7. Publish your project to npm, we don't use "npx progen release" for simplicity in skip some processes e.g. unused git diff and customized npm authentication
```bash
npm login
npm publish --access public
```

## Use the Construct
1. Create a new CDK project
```bash
mkdir my-intelli-agent
cd my-intelli-agent
npx projen new awscdk-app-ts
```

2. Add the new construct to your project
```bash
npm install intelli-agent
```

3. Import the construct in your stack
```typescript
import { IntelliAgentConstruct } from 'intelli-agent';
```

4. Use the construct in your stack
```typescript
new IntelliAgentConstruct(this, 'IntelliAgentConstruct', {
  // properties here
});
```

5. Build and deploy your project
```bash
npx projen build
npx cdk deploy
```

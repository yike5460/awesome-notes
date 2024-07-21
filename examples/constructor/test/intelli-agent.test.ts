// import { Hello } from '../src';

// test('hello', () => {
//   expect(new Hello().sayHello()).toBe('hello, world!');
// });

import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as IntelliAgent from '../src/intelli-agent-construct';

test('Intelli Agent Construct', () => {
  const app = new App();
  const stack = new Stack(app, 'TestStack');

  new IntelliAgent.AIAgent(stack, 'TestAIAgent', {
    agentName: 'TestAgent',
  });

  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::Lambda::Function', {
    Handler: 'index.handler',
    Runtime: 'nodejs18.x',
  });

  template.hasResourceProperties('AWS::ApiGateway::RestApi', {
    Name: 'TestAgent-API',
  });
});

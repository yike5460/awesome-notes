// custom_button.js

import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js';

function createButton(text, onClick) {
  const button = document.createElement('button');
  button.textContent = text;
  button.style.padding = '5px 10px';
  button.style.margin = '5px';
  button.addEventListener('click', onClick);
  return button;
}

function handleButtonClick() {
  // Call the backend Python function here
  // You can use the `api` module to make a request to the backend
  console.log('Button clicked! Calling backend function...');
  // Reboot system
}

const customButton = {
  name: 'CustomButton',
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name === 'Example') {
      const onCreated = nodeType.prototype.onCreated;
      nodeType.prototype.onCreated = function () {
        if (onCreated) {
          onCreated.call(this);
        }
        
        const button = createButton('Click me!', handleButtonClick);
        this.addWidget(
          'customButton', 
          'Custom Button',
          button,
          (ctx, node, widgetWidth, widgetY) => {
            // Position the button widget
            button.style.position = 'absolute';
            button.style.left = `${widgetWidth / 2 - button.offsetWidth / 2}px`;
            button.style.top = `${widgetY}px`;
          }
        );
      };
    }
  }
};

app.registerExtension(customButton);

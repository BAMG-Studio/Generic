import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Polyfill resizable ArrayBuffer / growable SharedArrayBuffer getters expected by jsdom deps
const abDescriptor = Object.getOwnPropertyDescriptor(ArrayBuffer.prototype, 'resizable');
if (!abDescriptor) {
  Object.defineProperty(ArrayBuffer.prototype, 'resizable', {
    get() {
      return false;
    },
  });
}

const sharedArrayBufferCtor = (globalThis as typeof globalThis & { SharedArrayBuffer?: typeof SharedArrayBuffer }).SharedArrayBuffer;
if (sharedArrayBufferCtor) {
  const sabDescriptor = Object.getOwnPropertyDescriptor(sharedArrayBufferCtor.prototype, 'growable');
  if (!sabDescriptor) {
    Object.defineProperty(sharedArrayBufferCtor.prototype, 'growable', {
      get() {
        return false;
      },
    });
  }
}

// Runs a cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});

// app/static/js/vendor/socketio.mjs
// FundChamps / Connect ATX Elite
// - ESM wrapper around socket.io-client
// - Safe defaults, CSP-safe
// - Legacy global (window.io) only once

import { io as _io, Manager, Socket } from "socket.io-client";

/**
 * io wrapper with hardened defaults.
 * @param {string|undefined} url
 * @param {import("socket.io-client").SocketOptions & import("socket.io-client").ManagerOptions} [opts]
 * @returns {import("socket.io-client").Socket}
 */
const io = (url, opts = {}) => {
  const defaults = {
    transports: ["websocket", "polling"],
    withCredentials: true,
  };
  return _io(url ?? undefined, { ...defaults, ...opts });
};

// Attach legacy global (once, safe, non-writable)
if (
  typeof window !== "undefined" &&
  !Object.prototype.hasOwnProperty.call(window, "io")
) {
  try {
    Object.defineProperty(window, "io", {
      value: io,
      configurable: false,
      enumerable: false,
      writable: false,
    });
  } catch {
    // Silent: SSR or locked globals
  }
}

export default io;
export { io, Manager, Socket };
export * from "socket.io-client";

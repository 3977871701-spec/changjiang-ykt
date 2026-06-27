// -*- coding: utf-8 -*-
/**
 * 雨课堂 超级防检测脚本 v1.0
 *
 * 反检测要点:
 * 1. 移除navigator.webdriver
 * 2. 删除Playwright/Selenium CDP注入变量
 * 3. 伪造Chrome runtime
 * 4. Canvas指纹随机化
 * 5. WebGL指纹伪造
 * 6. AudioContext指纹混淆
 * 7. 人类行为模拟 (需配合mouse_trail.py)
 */

// ── 1. 移除webdriver ──
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
    configurable: true,
    writeable: true
});
window.navigator.webdriver = undefined;

// ── 2. 删除Playwright/Selenium CDP注入变量 ──
const cdcProps = [
    'cdc_adoQpoasnfa76pfcZLmcfl_Array',
    'cdc_adoQpoasnfa76pfcZLmcfl_Promise',
    'cdc_adoQpoasnfa76pfcZLmcfl_Symbol',
    'cdc_adoQpoasnfa76pfcZLmcfl_JSON',
    'cdc_adoQpoasnfa76pfcZLmcfl_Object',
    'cdc_adoQpoasnfa76pfcZLmcfl_String',
    '$cdc_asdjflasutopfhvcZLmcfl_Array',
    '__webdriver_evaluate',
    '__selenium_evaluate',
    '__webdriver_script_function',
    '__webdriver_script_func',
    '__webdriver_script_nonce',
    'sfCommand', 'Skypoker', 'webdriver', 'selenium',
    '__webdriver_func', '__fxdriver_actor',
    '_WEBDRIVER_EVAL_CACHE', '__fxdriver_error',
    '__selenium_scriptLoaded', '__webdriver_script_name',
    '_selenium'
];
cdcProps.forEach(p => { try { delete window[p]; } catch(e) {} });

// ── 3. 伪造Chrome runtime ──
window.chrome = window.chrome || {};
window.chrome.runtime = {
    connect: () => ({ id: 'fake', name: 'fake', onDisconnect: {}, onMessage: { addListener: () => {} }, postMessage: () => {}, disconnect: () => {} }),
    sendMessage: () => {},
    sendNativeMessage: () => {},
    getManifest: () => ({ manifest_version: 3, name: 'Chrome', version: '120.0.0.0' }),
    getURL: (u) => u,
    id: 'yktfakeextensionid'
};
window.chrome.loadTimes = function() {
    return { commitLoadTime: '0.1', connectFinishTime: '0.05', connectionInfo: '1',
        dnsEndTime: '0.01', dnsStartTime: '0.005', domContentLoadedEventEnd: '0.3',
        domContentLoadedEventStart: '0.2', domLoading: '0.15', encodeBodySize: 0,
        finished: '0.4', firstPaintTime: '0.25', firstRenderTime: '0.2',
        loadType: 1, navigationType: 0, netBuildTime: '0.01', pushDocTime: '0.0',
        requestTime: '0.0', resourceLoadPriority: 1, resourceLoadTime: '0.1',
        sendEndTime: '0.002', sendStartTime: '0.001', showWidget: 1,
        ssl: '0.0', startLoadTime: '0.0', toDocumentLoaderEnd: '0.5',
        toDocumentLoaderStart: '0.0', toFirstCommit: '0.1', toNavigationStart: '0.0',
        transcriptOfFirstPaint: '0.0', transitionWorkDuration: '0.0',
        uspCookieBlockingTime: '0.0', wasAlternateProtocolAvailable: false,
        wasAssignerReliable: true, wasFetchedViaSpdy: false,
        wasNpnNegotiated: false, wasPrivacySandboxEnabled: false,
        wasProxyCredentialsFetched: false, wasSameProcessOnly: false,
        workerStartTime: '0.0' };
};
window.chrome.csi = function() {
    return { pageT: 'st', startE: '1', navType: '0', redirectE: '0', transTime: '350', url: location.href };
};
window.chrome.app = {
    getDetails: () => null, getIsInstalled: () => false, isInstalled: false,
    InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
    RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
};
window.chrome.webstore = { onInstallStateChanged: { addListener: () => {} }, getPersonCollection: () => {} };
window.chrome.storage = { local: { get: (k, cb) => cb({}), set: () => {}, remove: () => {} }, sync: { get: (k, cb) => cb({}), set: () => {}, remove: () => {} } };
window.chrome.tabs = { get: (id, cb) => cb(null), query: (q, cb) => cb([]), executeScript: () => {} };
window.chrome.commands = { getAll: (cb) => cb([]) };
window.chrome.i18n = { getMessage: () => '' };
window.chrome.variables = {};

// ── 4. Canvas指纹随机化 ──
const _origToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type, ...args) {
    try {
        const ctx = this.getContext('2d');
        if (ctx) {
            const id = ctx.getImageData(0, 0, this.width, this.height);
            const noise = Math.random() * 2 - 1;
            for (let i = 0; i < id.data.length; i += 4) {
                id.data[i] = Math.max(0, Math.min(255, id.data[i] + noise));
                id.data[i+1] = Math.max(0, Math.min(255, id.data[i+1] + noise));
                id.data[i+2] = Math.max(0, Math.min(255, id.data[i+2] + noise));
            }
            ctx.putImageData(id, 0, 0);
        }
    } catch(e) {}
    return _origToDataURL.apply(this, [type, ...args]);
};

const _origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
CanvasRenderingContext2D.prototype.getImageData = function(sx, sy, sw, sh) {
    const id = _origGetImageData.apply(this, arguments);
    if (id && id.data) {
        const noise = Math.random() * 1.5 - 0.75;
        for (let i = 0; i < id.data.length; i += 4) {
            id.data[i] = Math.max(0, Math.min(255, id.data[i] + noise));
            id.data[i+1] = Math.max(0, Math.min(255, id.data[i+1] + noise));
            id.data[i+2] = Math.max(0, Math.min(255, id.data[i+2] + noise));
        }
    }
    return id;
};

// ── 5. WebGL指纹伪造 ──
const _origGetParam = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(p) {
    const ANTI = {
        37445: 'Intel Open Source Technology Center',
        37446: 'Mesa Intel(R) UHD Graphics',
        35724: 'WebGL 2.0',
        34076: 30, 7936: 'OpenGL ES 2.0', 7937: 'OpenGL ES 2.0', 7938: 1,
        3379: 1, 3386: 1, 3410: 1, 3411: 4, 3412: 4, 3413: 8, 3414: 8,
        3415: 0, 4096: 8192, 4097: 8192, 4098: 8192, 4099: 8192,
        4100: 0, 4144: 2, 4145: 2, 4152: 1, 4153: 1, 4154: 0, 4155: 1
    };
    if (ANTI.hasOwnProperty(p)) return ANTI[p];
    try { return _origGetParam.apply(this, arguments); } catch(e) { return null; }
};

const _origExt = WebGLRenderingContext.prototype.getSupportedExtensions;
WebGLRenderingContext.prototype.getSupportedExtensions = function() {
    const ext = _origExt ? _origExt.apply(this) : [];
    if (!ext.includes('WEBGL_debug_renderer_info')) ext.push('WEBGL_debug_renderer_info');
    return ext;
};

// ── 6. AudioContext指纹混淆 ──
try {
    const _origGCD = AudioContext.prototype.getChannelData;
    if (_origGCD) {
        AudioContext.prototype.getChannelData = function(channel) {
            const buf = _origGCD.call(this, channel);
            if (buf && buf.length > 0) {
                const noise = (Math.random() - 0.5) * 0.0001;
                for (let i = 0; i < buf.length; i++) buf[i] = buf[i] + noise;
            }
            return buf;
        };
    }
} catch(e) {}

// ── 7. Function.toString检测防护 ──
const _knownNativeFuncs = new Set([
    'getChannelData','decodeAudioData','getImageData','toDataURL',
    'getParameter','getSupportedExtensions','querySelector','querySelectorAll',
    'getElementById','getContext','addEventListener','removeEventListener'
]);
const _origToString = Function.prototype.toString;
Function.prototype.toString = function(...args) {
    try {
        const name = this.name || '';
        if (_knownNativeFuncs.has(name) || name.startsWith('get') || name.startsWith('set')) {
            return `function ${name}() { [native code] }`;
        }
    } catch(e) {}
    return _origToString.apply(this, args);
};

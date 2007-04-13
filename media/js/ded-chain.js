/*
    * DED|Chain JavaScript Library (c) BSD License 2007
    * http://dedchain.dustindiaz.com/license.txt
    * Author: Dustin Diaz | http://www.dustindiaz.com
    * Website: http://dedchain.dustindiaz.com
    * V 0.2
*/
if ( typeof DED == 'undefined' ) {
    var DED = {};
}
// Sugar!
Function.prototype.method = function(name,fn) {
    this.prototype[name]=fn;
    return this;
};

if(!Array.prototype.forEach){Array. method('forEach',function(fn,thisObj){var scope=thisObj||window;for(var i=0,j=this.length;i<j;++i){fn.call(scope,this[i],i,this);}}). method('every',function(fn,thisObj){var scope=thisObj||window;for(var i=0,j=this.length;i<j;++i){if(!fn.call(scope,this[i],i,this)){return false;}}return true;}). method('some',function(fn,thisObj){var scope=thisObj||window;for(var i=0,j=this.length;i<j;++i){if(fn.call(scope,this[i],i,this)){return true;}}return false;}). method('map',function(fn,thisObj){var scope=thisObj||window;var a=[];for(var i=0,j=this.length;i<j;++i){a.push(fn.call(scope,this[i],i,this));}return a;}). method('filter',function(fn,thisObj){var scope=thisObj||window;var a=[];for(var i=0,j=this.length;i<j;++i){if(!fn.call(scope,this[i],i,this)){continue;}a.push(this[i]);}return a;}). method('indexOf',function(el,start){var start=start||0;for(var i=start,j=this.length;i<j;++i){if(this[i]===el){return i;}}return-1;}). method('lastIndexOf',function(el,start){var start=start||this.length;if(start>=this.length){start=this.length;}if(start<0){start=this.length+start;}for(var i=start;i>=0;--i){if(this[i]===el){return i;}}return-1;});}
(function() {
    // dandy shorthand mehtods
    var Dom = YAHOO.util.Dom;
    var Event = YAHOO.util.Event;
    var Connect = YAHOO.util.Connect;
    var Y = YAHOO.util;
    
    DED.register = function(REG) {
        function __$(el) {
            if ( YAHOO.lang.isUndefined(el) ) {
                // do nothing. 'sall good.
            }
            else if ( YAHOO.lang.isString(el) ) {
                this.el = Dom.query(el);
            } else {
                this.el = Dom.get(el);
            }
        };
        __$.method(REG.setStyle, function(prop, val) {
            Dom.setStyle(this.el, prop, val);
            return this;
        }).
        method(REG.getStyle, function(prop, fn) {
            fn.call(this, Dom.getStyle(this.el, prop));
            return this;
        }).
        method(REG.setCSS, function(styles) {
            for ( prop in styles ) {
                Dom.setStyle(this.el, prop, styles[prop]);
            }
        }).
        method(REG.getXY, function(fn) {
            fn.call(this, Dom.getXY(this.el));
            return this;
        }).
        method(REG.setXY, function(xy) {
            Dom.setXY(this.el, xy);
            return this;
        }).
        method(REG.fadeIn, function(o) {
            var that = this;
            this[REG.animate](
                {
                    opacity: {
                        from: 0,
                        to: 1
                    }
                },
                o.duration,
                Y.Easing.easeOutStrong,
                {
                    after: o.callback
                }
            );            
            return this;
        }).
        method(REG.fadeOut, function(o) {
            var that = this;
            this[REG.animate](
                {
                    opacity: {
                        from: 1,
                        to: 0
                    }
                },
                o.duration,
                Y.Easing.easeOutStrong,
                {
                    after: o.callback
                }
            );            
            return this;
        }).
        method(REG.animate, function(o, time, ease, cb) {
            var that = this;
            if ( cb.before ) {
                cb.before.call(this);
            }
            var a = new Y.ColorAnim(this.el, o, time, ease);
            if ( cb.after ) {
                var f = function() {
                    cb.after.call(that, a);
                };
                a.onComplete.subscribe(f);
            }
            a.animate();
            return this;
        }).
        method(REG.move, function(o, time, ease, cb) {
            var that = this;
            if ( cb.before ) {
                cb.before.call(this);
            }
            var a = new Y.Motion(this.el, o, time, ease);
            if ( cb.after ) {
                var f = function() {
                    cb.after.call(that, a);
                };
                a.onComplete.subscribe(f);
            }
            a.animate();
            return this;
        }).
        method(REG.addClass, function(c) {
            Dom.addClass(this.el, c);
            return this;
        }).
        method(REG.removeClass, function(c) {
            Dom.removeClass(this.el, c);
            return this;
        }).
        method(REG.replaceClass, function(oc, nc) {
            Dom.replaceClass(this.el, oc, nc);
            return this;
        }).
        method(REG.hasClass, function(c, fn) {
            fn.call(this, Dom.hasClass(this.el, c));
            return this;
        }).
        method(REG.toggle, function() {
            var method = function(el) {
                if ( Dom.getStyle(el, 'display') == 'none' ) {
                    Dom.setStyle(el, 'display', '');
                } else {
                    Dom.setStyle(el, 'display', 'none');
                }
            };
            Dom.batch(this.el, method);
            return this;
        }).
        method(REG.show, function() {
            Dom.setStyle(this.el, 'display', '');
            return this;
        }).
        method(REG.hide, function() {
            Dom.setStyle(this.el, 'display', 'none');
            return this;
        }).
        method(REG.setContent, function(html) {
            var method = function(el) {
                el.innerHTML = html;
            };
            Dom.batch(this.el, method);
            return this;
        }).
        method(REG.create, function(el, o, cb) {
            var el = document.createElement(el);
            for ( prop in o ) {
                if ( YAHOO.lang.hasOwnProperty(o, prop) ) {
                    el.setAttribute(prop, o[prop]);
                }
            }
            if (cb) {
                cb.call(this, el);
            }
            return this;
        }).
        method(REG.append, function(element) {
            Dom.batch(this.el, function(el) {
                el.appendChild(element);
            });
            return this;
        }).
        method(REG.on, function(type, fn, stop) {
            var that = this;
            Dom.batch(this.el, function(el) {
                var f = function(e, el) {
                    if (stop) {
                        Event.stopEvent(e);
                    }
                    fn.call(that, el, e);
                }
                Event.on(el, type, f, el);
            });
            return this;
        }).
        method(REG.hijackForm, function(cb) {
            var that = this;
            var frm = this.el[0];
            this[REG.on]('submit', function(e) {
                Event.preventDefault(e);
                Connect.setForm(frm);
                if ( cb.before ) {
                    cb.before.call(this);
                }
                Connect.asyncRequest('POST', frm['action'], {
                    success: function(resp) {
                        if ( cb.after ) {
                            cb.after.call(that, resp.responseText);
                        }
                        if ( cb.populate ) {
                            Dom.get(cb.populate).innerHTML = resp.responseText;
                        }
                    },
                    failure: function(resp) {
                        if ( cb.failure ) {
                            cb.failure.call(that, resp);
                        }
                    },
                    timeout: 20000
                });
            });
            return this;
        }).
        method(REG.repeat, function(time, repeatid, fn) {
            var that = this;
            this.time = (time || 1) * 1000;
            var f = function() {
                fn.call(that);
            };
            this.repeatid = window.setInterval(f, this.time);
            return this;
        }).
        method(REG.stopRepeat, function() {
            window.clearTimeout(this.repeatid);
            return this;
        }).
        method(REG.fetch, function(uri, cb) {
            var that = this;
            if ( cb.before ) {
                cb.before.call(this);
            }
            Connect.asyncRequest('GET', uri, {
                success: function(o) {
                    cb.after.call(that, o.responseText);
                },
                failure: function(o) {
                    YAHOO.log('failed request: '+o, 'warn');
                },
                timeout: 20000
            });
            return this;
        }).
        method(REG.populate, function(uri) {
            var that = this;
            Connect.asyncRequest('GET', uri, {
                success: function(o) {
                    that[REG.setContent](o.responseText);
                },
                failure: function(o) {
                    YAHOO.log('failed request: '+o, 'warn');
                },
                timeout: 20000
            });
            return this;
        }).
        method(REG.throttle, function(time, haystack, o) {
            var that = this;
            this.throttleid = o.id;
            this.time = (time || 5) * 1000;
            this.loop = o.loop || false;
            this.repeated = 0;
            this.total = 0;
            var hay = [];
            if ( haystack instanceof Array ) {
                this.total = haystack.length;
                hay = haystack;
            } else if ( haystack instanceof Object ) {
                for ( key in haystack ) {
                    if ( YAHOO.lang.hasOwnProperty(haystack, key) ) {
                        hay[this.total++] = {
                            "key": key,
                            "value": haystack[key]
                        };
                    }
                }
            }
            var f = function() {
                if ( that.repeated === that.total ) {
                    if ( o.onComplete ) {
                        o.onComplete.call(that);
                    }
                    if ( that.loop ) {
                        that.repeated = 0;
                    } else {
                        window.clearInterval(window[REG.namespace].throttlers[that.throttleid]);
                        return;
                    }
                }
                var needle = hay[that.repeated];
                o.callback.call(that, needle);
                that.repeated++;
            };
            o.callback.call(that, hay[0]);
            that.repeated++;
            window[REG.namespace].throttlers[this.throttleid] = window.setInterval(f, this.time);
            return this;
        }).
        method(REG.stopThrottle, function(throttleid) {
            window.clearInterval(window[REG.namespace].throttlers[throttleid]);
            return this;
        }).
        method(REG.pluck, function(attribute, delimeter, fn) {
            var map = this.el.map(function(el) {
                if ( el.getAttribute(attribute) ) {
                    return el[attribute];
                }
            });
            if ( delimeter ) {
                fn.call(this, map.join(delimeter));
            } else {
                fn.call(this, map);
            }
            return this;
        });
        
        window[REG.namespace] = function(el) {
            return new __$(el);
        };
        window[REG.namespace].throttlers = {};
        window[REG.namespace].extend = YAHOO.extend;
        window[REG.namespace].augment = YAHOO.augment;
        
        
        // sugar array shortcuts
        window[REG.namespace].forEach = Array.prototype.forEach;
        window[REG.namespace].every = Array.prototype.every;
        window[REG.namespace].some = Array.prototype.some;
        window[REG.namespace].map = Array.prototype.map;
        window[REG.namespace].filter = Array.prototype.filter;
        
        DED.extendChain = function(name, fn) {
            __$.method(name, fn);
        };
    };
})();

DED.register({
    namespace : '_$',
    addClass: 'addClass',
    animate: 'animate',
    append: 'append',
    create: 'create',
    fadeIn: 'fadeIn',
    fadeOut: 'fadeOut',
    fetch: 'fetch',
    getStyle: 'getStyle',
    getXY: 'getXY',
    hasClass: 'hasClass',
    hide: 'hide',
    hijackForm: 'hijackForm',
    move: 'move',
    on: 'on',
    pluck: 'pluck',
    populate: 'populate',
    removeClass: 'removeClass',
    repeat: 'repeat',
    replaceClass: 'replaceClass',
    setContent: 'setContent',
    setCSS: 'setCSS',
    setStyle: 'setStyle',
    setXY: 'setXY',
    show: 'show',
    stopRepeat: 'stopRepeat',
    stopThrottle: 'stopThrottle',
    throttle: 'throttle',
    toggle: 'toggle'
});
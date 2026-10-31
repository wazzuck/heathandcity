"use strict";

function _instanceof(left, right) { if (right != null && typeof Symbol !== "undefined" && right[Symbol.hasInstance]) { return !!right[Symbol.hasInstance](left); } else { return left instanceof right; } }
function _classCallCheck(instance, Constructor) { if (!_instanceof(instance, Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }
function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }
function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var CookiePolicy = function () {

    function CookiePolicy() {
        _classCallCheck(this, CookiePolicy);
        _defineProperty(this, "initiated", false);
        _defineProperty(this, "analytics", false);
        _defineProperty(this, "settings", false);

        this.domain = "." + window.location.hostname.replace("www.", "");
        this.initCookie();

        if (!this.initiated) {
            jQuery("#cookiepolicy").css("display", "block");
        }
    }

    _createClass(CookiePolicy, [
        {
            key: "initCookie",
            value: function initCookie() {
                var cookie = document.cookie.match(/cookiepolicy=({.*?})/);

                if (cookie) {
                    cookie = JSON.parse(cookie[1]);
                    this.analytics = cookie.analytics;
                    this.settings  = cookie.settings;
                    this.initiated = true;
                } else {
                    this.deleteSettingsCookies();
                    this.deleteAnalyticsCookies();
                }

                this.append();
            }
        },
        {
            key: "append",
            value: function append() {
                if (jQuery("#top-info").length) {
                    jQuery("#cookiepolicy").prependTo("#top-info");
                } else {
                    jQuery("#cookiepolicy").prependTo("body");
                }
            }
        },
        {
            key: "setCookie",
            value: function setCookie(name, value) {
                var expiration = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : "";

                if (!_instanceof(expiration, Date)) {
                    var date = new Date();
                    var expirationDays = expiration;
                    expiration = new Date();
                    expiration.setTime(date.getTime() + expirationDays * 24 * 60 * 60 * 1000);
                }

                document.cookie = name + "=" + value + ";expires=" + expiration.toUTCString() + ";path=/;domain=" + this.domain;
            }
        },
        {
            key: "getCookie",
            value: function getCookie(name, type) {
                var cookiesAllowed = false;

                cookiesAllowed = type == "analytics" && this.analytics == true ? true : cookiesAllowed;
                cookiesAllowed = type == "settings"  && this.settings  == true ? true : cookiesAllowed;

                if (cookiesAllowed) {
                    var regex = new RegExp(name + "=([^;]*)");
                    var cookie = document.cookie.match(regex);
                    return cookie ? cookie[1] : false;
                }

                return false;
            }
        },
        {
            key: "deleteCookie",
            value: function deleteCookie(name) {
                document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/;domain=" + this.domain;
                document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/;";
            }
        },
        {
            key: "deleteSettingsCookies",
            value: function deleteSettingsCookies(name) {
                document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/;domain=" + this.domain;
                var cookies = document.cookie.match(/[a-zA-Z0-9-_]+=/g);

                if (cookies) {
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = cookies[i].replace(/=$/, "");

                        if (["_ga", "_gat", "_gid", "cookiepolicy"].indexOf(cookie) == -1) {
                            this.deleteCookie(cookie);
                        }
                    }
                }
            }
        },
        {
            key: "deleteAnalyticsCookies",
            value: function deleteAnalyticsCookies() {
                this.deleteCookie("_ga");
                this.deleteCookie("_gat");
                this.deleteCookie("_gid");
            }
        },
        {
            key: "saveCookies",
            value: function saveCookies(analytics, settings) {
                this.analytics = analytics;
                this.settings = settings;
                var expiration = analytics && settings ? 365 : 30; // Cookie lasts 365 days if user accepts all, or 30 days if denies any option

                this.setCookie("cookiepolicy", JSON.stringify({
                    analytics: analytics,
                    settings: settings
                }), expiration);

                if (!settings)
                    this.deleteSettingsCookies();

                if (!analytics)
                    this.deleteAnalyticsCookies();
                else if (typeof initGoogleAnalytics == "function")
                    initGoogleAnalytics();
            }
        },
        {
            key: "setEmergencyPopup",
            value: function setEmergencyPopup() {
                if (jQuery("#emergency-popup-script").length && !this.getCookie("emergency-popup", "settings")) {
                    var date = new Date();
                    var expiration = new Date(date.getFullYear() + "-" + date.getMonth() + 1 + "-" + date.getDate() + " 23:59:59");
                    this.setCookie("emergency-popup", expiration);
                }
            }
        }
    ]);

    return CookiePolicy;
}();

jQuery(document).ready(function ($) {
    var cookiePolicy = new CookiePolicy();

    if ($("#cookie-settings").length) {
        if (cookiePolicy.analytics || !cookiePolicy.initiated)
            $("#analytics-cookie-on").prop("checked", true);
        else
            $("#analytics-cookie-off").prop("checked", true);

        if (cookiePolicy.settings || !cookiePolicy.initiated)
            $("#settings-cookie-on").prop("checked", true);
        else
            $("#settings-cookie-off").prop("checked", true);
    }

    $("#accept-cookies").on("click", function () {
        cookiePolicy.saveCookies(true, true);

        $("#cookiepolicy").slideUp();

        if (cookiePolicy.settings)
            cookiePolicy.setEmergencyPopup();
    });

    $("#save-cookies").on("click", function () {
        var analytics = $("#analytics-cookie-on").is(":checked");
        var settings = $("#settings-cookie-on").is(":checked");
        cookiePolicy.saveCookies(analytics, settings);

        $("#cookiepolicy").slideUp();

        if (cookiePolicy.settings)
            cookiePolicy.setEmergencyPopup();

        if (!$("#cookie-alert").length) {
            $("<div id='cookie-alert' class='frm_message'>Your cookie settings were saved.</div>").insertAfter("#save-cookies");
        }

        $("#cookie-alert").attr("tabindex", "0").focus();
        setTimeout(function () {
            $("#cookie-alert").removeAttr("tabindex");
        }, 500);
    });

    $("#cookie-settings input[type=radio]").on("change", function () {
        $("#cookie-alert").remove();
    });
});
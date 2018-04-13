javascript-diacritics-utility (JDU)
=========================

Overview
--------

Javascript Utility to test for and remove accents/diacritics in strings

Getting started
---------------

### Download

- [Download](https://github.com/mk7upurz87/jdu/archive/master.zip) from github.
- install from bower: bower i jdu
- install from npm: npm i jdu

### Install from bower
```
bower install jdu
```


### Load Script
Load the script file: `remove-diacritics.js` in your application:

```html
<script type="text/javascript" src="bower_components/jdu/jdu.js"></script>
```

### Code
Use JDU in your application to create the object:

```js
window.jdu.replace("some string with diacritics");
```
or with require
```js
var jdu = require('jdu');
jdu.replace("some string with diacritics");
```

# 前端学习小记

[TOC]

## JS

### document对象

#### 获取元素

- `getElementsByTagName` ：通过标签名查找，如`document.getElementsByTagName('p')`
- `getElementsByClassName`：通过`class`查找
- `getElementsByName`：通过`name`属性查找（例如`<form>`、`<radio>`、`<img>`等标签具有`name`属性）

以上方法都会返回一个类似数组的对象。

- `getElementById`：通过`id`属性查找，只会返回一个元素而非数组，需要注意这里Element后面没有s
- `querySelector`：中间填写CSS选择器，如`'.myclass'`、`'#myid'`等，返回满足条件的第一个元素
- `querySelectorAll`：同样填写CSS选择器，返回所有满足条件的元素

#### 创建元素

- `var x = document.createzElement('div');` 标签类型
- `var y = document.createTextNode('HelloWorld');` 文本类型
- `x.appendChild(y);` （`appendChild`既可以塞文本，也可以塞元素）
- `var z = document.createAttribute('id');` 属性类型
- `z.value = 'myid';` 通过`.value`为属性赋值
- `x.setAttributeNode(z);`
- 若存下从原网页中获取到的标签并进行修改，那么会直接体现在网页上。

### Element对象

#### 属性

- `id`
- `className`：空格隔开的字符串
- `classList`：数组
- `innerHTML`
- `innerText`

```js
var x = document.getElementByTagName('p')[0];
console.log(x.id);
x.id = 'myid';
console.log(x.className);
x.className = 'myclass1 myclass2';
console.log(x.classList);
x.classList.add('myclass3');
x.classList.remove('myclass2');
if (x.classList.contains('myclass3')) {
    console.log('contains myclass3');
}
//.toggle()：移入或移出
x.innerHTML = '<a href='www.baidu.com'>HelloWorld<a>';
x.innerText = 'HelloWorld';
//两者都是替换内容，区别在于innerHTML可以识别HTML格式
```

#### 获取元素位置

- `Element.clientHeight`，`Element.clientWidth`：获取元素的`padding`在内的尺寸，不包括`border`和`margin`
- 用`document.documentElement.clientHeight`获取视口高度（屏幕高度）
- 用`document.body.clientHeight`获取页面高度
- `scrollHeight`类似，但不包含溢出部分，实际运用中没有溢出就区别不大
- `scrollLeft`和`scrollHeight`获取水平滚动的距离和垂直滚动的距离
- `offsetHeight`和`offsetWidth`获取包含`padding`和`border`的宽度
- `offsetLeft`和`offsetTop`获取到定位父级左边界/上边界的间距（需要relative）

### CSS操作

- 通过节点的`Attribute`修改
  ```js
  div.setAttribute(
    'style',
    'background-color: red;' + 'border: 1px solid black;'
  );
  ```
- 通过`.style`修改
  ```js
  var y = x.style;
  y.backgroundColor = 'red';
  y.border = '1px solid black';
  ```
- 通过`cssText`属性修改
  ```js
  y.cssText = 'background-color: red;' + 'border: 1px solid black;';
  ```

### 事件处理

#### HTML事件

在`button`中写`<button onclick="demo()">按钮</button>`，然后定义函数：
```js
function demo() {
  alert("hello world");
}
```

缺点：HTML和JS没有分开

#### DOM0级事件

在`button`中写`<button id="btn">按钮</button>`，然后通过id找到元素并指定元素的`.onclick`：
```js
var btn = document.getElementById("btn");
btn.onclick = function() {alert("hello world");};
```
缺点：无法同时添加多个事件

#### DOM2级事件
```js
btn.addEventListener("click", function() {
  alert("hello world");
});
```
add多个事件时，事件不会被覆盖

#### 更多鼠标事件

![](https://images.cnblogs.com/cnblogs_com/Hany01/1830836/o_230815032008_%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202023-08-15%20111914.jpg)

使用时在前面加上`on`即可，例如`btn.ondbclick=function(){}`

#### Event 事件对象

事件发生后，会产生一个事件对象，作为参数传给监听函数，例如：
```js
btn.onclick = function(e) {
  console.log(e);
};
```

对象属性：
- `Event.Target`：得到被执行动作的标签块
  例如我可以这样，在点击之后修改按钮的文本内容：
  ```js
  btn.onclick = function(e) {
    e.target.innerHTML = '点击之后';
  };
  ```
- `Event.type`：得到事件类型，如`click`等

对象方法：
- `Event.preventDefault()`：取消浏览器对事件的默认行为，如链接跳转，我们在给链接指定`onclick`的动作后，点击后不仅会执行`onclick`的动作，也会跳转，我们可以通过这个方法避免跳转。
- `Event.stopPropagation()`：比如我们在点击子结点的时候，默认会同时执行子结点和父结点的动作，如果我们不想执行父结点的动作，就需要在子结点执行动作之前使用`e.stopPropagation()`、防止事件冒泡。

#### 键盘事件

- `keydown`：按下时触发
- `keypress`：按下有值的键时触发
- `keyup`：松开时触发

`e.keyCode`获取值，可以与ASCII码对应，回车为13

#### 表单事件

- `input`：输入

  ```js
  var x = document.getElementById('username');
  username.oninput = function(e) {
      console.log(e.target.value); //.target获取Element对象，.value获取输入内容
  }
  ```

- `select`：选中，即鼠标拖动选中输入框内的文本（用得不多）

- `change`：与`input`的区别在于，不会连续触发，只有在修改完成（回车/失去焦点）时才会触发

- `reset`：重置

  ```js
  var x = ducument.getElementById('myform');
  ```

  使用`x.reset();`即可清空表单内容。

- `submit`：提交
  （`reset`和`submit`两个事件发生在表单对象`<form>`上、而不是表单的成员上）

#### 事件代理（事件委托）

事件会在冒泡阶段向上传播到父节点，因此可以把子结点的监听函数定义在父节点上，由父节点的监听函数统一处理多个子元素的事件。

```html
<ul id='list'>
    <li>li1</li>
    <li>li2</li>
    <li>li3</li>
</ul>
```

```js
var list = document.getElementById('list');
list.addEventListener('click', function(e){
    if (e.target.tagName.toLowerCase() == 'li') { //.target获取被点击的子节点，.tarName获得'LI'，.toLowerCase()获得'li'
        console.log(e.target.innerHTML);
    }
});
```

### 定时器

- `setTimeout`：用于指定某段代码或某个函数在多少毫秒之后执行，返回一个整数，表示定时器的编号，可用于后续取消。
  格式：`var id = setTimeout(代码/函数, delay);`
  例如：`setTimeout(function(){console.log('x')}, 1000);`
  需要注意的是：如果回调函数是对象的方法，那么`setTimeout`使得方法内部的`this`关键字指向全局环境，而不是定义时所在的对象。
  取消定时器：`clearTimeout(id);`
- `setInterval`：使用方法类似，区别在于效果是每隔一段时间就执行一次。
  可以直接在内部使用`clearInterval();`来终止。

### 性能优化

#### 防抖

比如我们设置一个`onscroll`，每次滚动都会触发，这样我们的执行频率就会非常高，下滑一次会执行很多次。

为了解决这个问题，我们可以采用这样的策略：

- 若在x ms内没有再次触发事件，则执行函数
- 若在x ms内被再次触发，则当前计时取消，重新开始计数

这样，我们在短时间内大量触发同一事件，就只会执行一次。

具体用`setTimeout`来实现。

```js
function debounce(fn, delay) {
    var timer = null;
    return function() {
        if (timer) { //如果定时器存在，那么清空，并在下面重新开始计时
            clearTimeout(timer);
        }
        timer = setTimeout(fn, delay); //开始计时
    };
}
```

#### 节流

上面的防抖操作的缺点在于，如果我们一直触发同一事件，在此期间内就一直不能够执行操作，只有等最后一次触发结束后才能得到执行。

```js
function throttle(fn, delay) {
    var valid = true;
    return function() {
        if (!valid) {
            return false;
        }
        valid = false;
        setTimeout(function(){
            fn();
            valid = false;
        });
    };
}
```

## ES6

ES是JS的规格，JS是ES的一种实现，日常场合中这两个词可互换。 	

### let

- `var`的作用域是所在函数；`let`的作用域是所在块（大括号）
- `let`不存在*变量提升*（`var`的定义是可以放在使用之后的）

### 常量

`const`声明的变量只在块级作用域中有效、且同样不存在变量提升（跟`let`类似）

### 对象的解构赋值

```js
var user = {name: 'hy', age: 21};
let {name, age} = user;
```

注意：赋值没有次序，也不要求取出全部的属性，但是变量必须与属性同名，才能取到正确的值。（也就是属性是`name`和`age`，变量命名也得是`name`和`age`）

函数同样可以取出赋值，例如：

```js
var {log} = console;
var {abs, ceil, floor, random} = Math;
```

对于已声明的变量用于解构赋值，必须小心，正确用法如下：

```js
let hello = "hello";
({hello} = {hello: "hello!"});
```

### 字符串扩展

#### Unicode

ES6增强了对字符的支持，允许用`\uxxxx`表示字符，其中`xxxx`为Unicode码点。

#### 字符串遍历接口

```js
for (let i of 'abcd') { //注意是of
    console.log(i);
}
```

#### 模板字符串

当我们需要将一些字符串与变量拼接起来的时候，可以直接使用加法，但是写起来有些麻烦，于是可以使用模板字符串，它用反引号标识：

```js
let url = "www.baidu.com";
let code = `<a href='${url}'>BAIDU</a>`;
//等价于"<a href='" + url + "'>BAIDU</a>"
```

#### 新增字符串方法

- `s.includes(t)`：返回是否找到子串
- `s.startsWith(t)`：返回是否是头部
- `s.endsWith(t)`：返回是否是尾部

以上三个函数都支持第二个参数`pos`，表示从哪个地方开始找，`s.includes(t, pos)`。

- `s.repeat(x)`：返回将`s`重复`x`次拼接而成的字符串
- `s.padStart(len, t)`：在`s`前面补若干个`t`、直到长度为`len`
- `s.padEnd(len, t)`：在`s`后面补若干个`t`，直到长度为`len`
- `s.trim()`：去掉首尾空字符的结果
- `s.trimStart()`：去掉开头空字符的结果
- `s.trimEnd()`：去掉结尾空字符的结果
- `s.at(x)`：第`x`个字符，支持负数索引

### 数组扩展

#### 扩展运算符

由三个点`...`组成，用于将数组转化为用逗号分开的参数序列。

`console.log(...[1, 2, 3]);`相当于`console.log(1, 2, 3);`

通过`...`，我们可以用`[...arr1, ...arr2]`代替`arr1.concat(arr2)`

ES5求最大值：`Math.max.apply(null, arr)`

ES6求最大值：`Math.max(...arr)`

#### 新增方法

- `Array.from`：将类数组转化为数组

  - `arguments`

    ```js
    function fn() {
        console.log(arguments); //[1, 2, 3]
        console.log(arguments[0]); //1
    }
    fn(1, 2, 3);
    ```

    `arguments`是伪数组，只能使用读取方法和`length`属性，不能使用数组方法

  - 元素集合

    例如`var x = document.querySelectorAll('h3');`

  - 类似数组的对象

    ```js
    var obj = {
        "0": "x",
        "1": 233,
        "2": true
    };
    ```

  以上类数组均可通过`Array.from(arr)`得到数组

- `Array.of`：将一组值转化为数组

  如`Array.of(1, 2, 3)`，就相当于`[1, 2, 3]`

  （补充：`Array(3)`相当于`[ , , ]`）

### 对象扩展

#### 简洁表示

在大括号中可以直接写变量和函数，例如：

```js
var name = 'hany01';
var user = {
    name,
    age: 21,
    gender: 'male',
    getName() {
        console.log(this.name);
    }
};
```

#### 属性名表达式

ES6允许字面量定义对象时，用表达式作为对象的属性名，放在方括号内即可。

```js
let key = 'key1';
let obj = {
    [key]: 1,
    ['ke'+'y2']: true
};
```

### 函数扩展

我们之前定义函数有两种方法：

```js
function fn1() {
    //...
}
var fn2 = function() {
    //...
}
```

#### 箭头函数

- 有且只有一个参数时可省略括号
- 可写成大括号包起来的形式
- 如果箭头函数返回的是对象，则一定要加小括号

```js
var fa = () => 10;
var fb = x => x;
var fc = (x, y) => x+y;
var fd = (x, y) => {
    var z=x+y;
    return z;
};
var fe = () => ({x: 10, y: 20});
```

需要注意的是，对于一般函数来说，内部的`this`指向函数所在的对象，比如`setTimeout`就是整个window。

但是这点在箭头函数中不成立，箭头函数里面写的`this`引用的就是定义时上层作用域中的`this`。比如你在`setTimeout`中写箭头函数，`this`指的就是所在对象而非window。

### Set

跟C++ std中的类似，值可以是不同类型的，但不能是重复的。

```js
var s = new Set(); //用new创建
s.add(2); //用add方法添加数据
s.add(3);
s.delete(2); //用delete方法删除数据，返回布尔值表示是否删除成功
if (s.has(3)) { //用has方法检查是否存在
    console.log("exists");
}
s.clear(); //用clear方法清空
var s1 = new Set([1, 2, 3]); //将一个数组作为初始集合
//用扩展运算符变回数组：[...s1]
//因此可以用set来实现去重：[...new Set(array)]
var s2 = new Set('abbc'); //也可以接收字符串
```

### Promise对象

是异步编程的一种解决方案，比传统方法（回调函数和事件）更合理、强大。

简单来说，是保存了某个未来结束的某个事件的结果。

Promise提供了统一的API，各种异步操作都可以用同样的方法进行处理。将异步操作以同步操作的流程表达出来，避免了层层嵌套的回调函数。

#### 基本用法

`Promise`对象是一个构造函数，用来生成`Promise`实例。

```js
const promise = new Promise(function(resolve, reject) { //经常用const，因为我们一般不会重新赋值
    //...
    if (/*success*/) {
    	resolve(value);
    } else {
    	reject(value);
    }
});
```

`Promise`构造函数接收一个函数作为参数，该函数具有`resolve`和`reject`两个参数，它们是两个函数，由JS提供，无需自己部署。

实例生成后，可以使用`then`方法分别指定`resolved`状态和`rejected`状态的回调函数。

```js
promise.then(function(value) {
    //success
}, function(error) {
    //failure
});
```

对于上述写法了解即可，在框架中一般可以用现成的。

### Async函数

`async`函数可将异步操作变为同步操作。

比如说，`setTimeout`定时器是异步的，先`setTimeout`定时输出内容a，再输出内容b。实际效果是先输出b，再输出a。

用法：放在函数的最前面，在具有异步操作的代码前面放入`await`

### Class

ES5的写法：

```js
function Person(name, age) {
    this.name = name;
    this.age = age;
}
Person.prototype.getName = function() {
    console.log(this.name);
}
var p = new Person('hany01', 21);
p.getName();
```

ES6提供了更加接近传统语言的写法。

```js
class Point {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
    toString() {
        return '(' + this.x + ',' + this.y + ')';
    }
    static print() { //静态方法，通过类调用而非通过实例调用；其中的this指的是类而非实例 
        console.log("hello world");
    }
}
var p = new Point(1, 2);
console.log(p.toString());
class Point_ extends Point { //继承，享有父亲的属性和方法
    constructor(x, y, z) {
        super(x, y);
        this.z = z;
    }
}
```

### Module

将js代码写在不同的文件中。

- `export`导出变量和函数

  ```js
  export var x = 1;
  export var y = 'hello world';
  export function add(x, y) {
      return x + y;
  }
  ```

- `import`引入

  ```js
  import {x, y, add} from "./xx.js"
  ```

  可以改名后引入：

  ```js
  import {x, y, add as add1} from "./xx.js"
  ```

- `export default`默认导出

  ```js
  export default function() {
      console.log('hahaha');
  }
  ```

  ```js
  import CustomName想取什么名字就取什么名字 from "./xx.js"
  CustomName();
  ```

  一个文件中只能有一个`export default`
+++
date = "2017-02-18T05:35:59+08:00"
title = "Lua C API 简介"
tags = ["lua"]
series = ["Lua C API"]
+++

公司主要用 skynet 和 cocos2d-x Lua 来开发游戏。两者都采用了嵌入 Lua 来开发。因为性能，以及和原生代码交互，就需要在 Lua 和其它语言之间进行交互。最近做了挺多这样的工作，积累了一些心得，会陆续总结分享出来。

这一篇是 Lua C API 的简单介绍。

<!--more-->

使用 Lua C API 有两个场景。一是把 Lua 嵌入在其它语言中，只要能链接 C 库并调用 C 方法都可以使用。另一种是开发 Lua C 模块。

## Lua C API

先以在 C 中嵌入 Lua 为例说明。下面是初始化 Lua 虚拟机环境并执行一段 Lua 代码的例子。

{{% codecaption name="lua-c-api-template" link="https://coding.net/u/doitian/p/lua-c-api-intro/git/blob/master/lua-c-api-template.c" %}}

~~~ c
#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

#define QUOTE(...) #__VA_ARGS__
static const char *lua_code = QUOTE(
  print("Hello, Lua C API")
);

int main(int argc, char* argv[]) {
  int status = 0;

  lua_State *L = luaL_newstate();
  luaL_openlibs(L);

  status = luaL_loadstring(L, lua_code) || lua_pcall(L, 0, 0, 0);
  if (status) {
    fprintf(stderr, "%s", lua_tostring(L, -1));
    lua_pop(L, 1);
  }

  lua_close(L);
  return status;
}
~~~

上面代码要求使用至少 Lua 5.1，否则 `luaL_newstate` 需要改成 `lua_open`, `luaL_openlibs` 要拆成单独的各个标准库加载方法比如 `luaopen_io`。

编译需要引用 Lua 头文件并链接 Lua 库，本文所有示例和编译脚本都放在[这个 Git 仓库][git_repo]中。

Lua C API 的核心就是操作栈，所有的操作都是通过栈实现的。访问栈可以用正数或者负数。每次函数调用会标记当前栈顶的位置，之后压入的元素位置从 1 开始。下面会提到函数的参数会首先压入栈，所以正数 i 引用的栈位置就是第 i 个参数。负数就是从栈顶开始数的位置，-1 就是栈顶元素，-2 就是栈顶下面一个元素，依此类推。

使用栈要注意，谁负责压入就要负责弹出，很多 Lua C API 出现错误都是栈操作不当引起的。

{{% figure src="/images/201702/lua-stack.png" link="/images/201702/lua-stack.png" title="Lua 栈" %}}

查看 C API 的文档主要要查看是不是有参数需要压入栈，执行后是否会从栈顶弹出元素。

::举例 C API::

下面以通过设置全局变量为例来说明如何使用 C API

::例子 全局变量::

## Lua C Function

上面的例子用到了 integer, float, boolean, string, table 等数据类型，以及在 C 中调用 Lua 方法。

最常用的还有在 C 中定义个方法，可以在 Lua 中被调用。

一个 Lua 的 C 方法参数和返回类型如下。

::lua c 方法 prototype::

上面提到过，方法开始时调用参数会依次压入栈，返回时要把返回结果依次压入栈并将结果数量做为 C 函数返回值。没有返回结果的话直接返回 0 即可。

::lua c 方法示例和图::

因为 C Function 不是在 Lua 中定义了的，也就没办法通过闭包访问定义函数时所在地方可见的栈变量。不过可以通过 `lua_pushcclosure` 来显式创建需要通过闭包访问的变量。

::closure sample::

## Lua C Module

上面都是以嵌入 Lua 直接操作栈来进行交互，接下来说明如果用 C 来实现一个模块可以在 Lua 中 `require`。

其实一个 C Module 就是一个用 C 写的动态链接库。如果想通过

	require “cmodule"

来使用，动态链接库文件名字就必须是 cmodule (cmodule.so 或者 cmodule.dll 等等)，并放在 `LUA_CPATH` 指定的目录中。动态链接库需要定义 Lua C Function，方法名必须是 `luaopen_cmodule`，这个方法的访问结果就是 `require "cmodule"` 的返回结果。

::c moduel sample::

像在 cocos2d-x 中，单独编译动态链接库并不是个很方便的选择，因为必须为所有可能用到的平台都生成对应的动态库，这种情况下可以把 C 代码和项目一起编译，使用 Lua C API 来注册。

一般会用到两种方法。

一种是 cocos2d-x Lua 中采用的直接把模块应该返回的 table 注册成全局变量，使用时不需要 `require` 直接用全局变量就可以了，所以有一堆的全局变量，`cc`, `display` 等等。

然后滥用全局变量会有很多问题，luacheck 静态检查工具需要手动加入例外像，造成 `_G` 表查找变慢等等。其实 Lua 提供了很好的解决方案，一个是 `package.loaded`，一个是 `package.preload`。

表 `package.loaded` 是所有通过 `require` 加载过模块的返回值。重复 `require` 会直接返回 `package.loaded` 中以模块名为 key 的值。如果使用 C API 直接把模块的返回值以模块名为 key 添加到这个表在，那么 `require` 就会返回预先填入的值。不过这种方法有个问题就是一般在开发环境中会实现代码重新加载的功能，这个功能一般就是清空 `package.loaded`，这样之后的 `require` 就会重新从文件中读取，所有需要手动排除这些预先插入的模块。

而 `package.preload` 才是推荐的做法。这个表也是使用模块名为 key，不过对应 的值必须是 Lua 方法或者 C Function。当 `package.loaded` 查找失败后，`require` 会优先查找 `package.preload` 这个表，如果找到了对应的 key，则会调用其对应的方法，而方法的访问值就作为 `require` 的访问值，并同时插入到 `package.loaded` 中。

::package.preload sample::

[git_repo]: https://coding.net/u/doitian/p/lua-c-api-intro/git

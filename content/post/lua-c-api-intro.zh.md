+++
date = "2017-02-18T05:35:59+08:00"
title = "Lua C API 简介"
tags = ["lua"]
series = ["Lua C API"]
toc = "right"
+++

公司主要用 skynet 和 cocos2d-x Lua 来开发游戏。两者都采用了嵌入 Lua 来开发。因为性能，以及和原生代码交互，就需要在 Lua 和其它语言之间进行交互。最近做了挺多这样的工作，积累了一些心得，会陆续总结分享出来。

这一篇是 Lua C API 的简单介绍。

<!--more-->

使用 Lua C API 有两个场景。一是把 Lua 嵌入在其它语言中，只要能链接 C 库并调用 C 方法都可以使用。另一种是开发 Lua C 模块。

## Lua C API

先以在 C 中嵌入 Lua 为例说明。下面是初始化 Lua 虚拟机环境并执行一段 Lua 代码的例子。

{{% codecaption name="lua-c-api-template.c" link="https://coding.net/u/doitian/p/lua-c-api-intro/git/blob/master/lua-c-api-template.c" %}}

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

{{% /codecaption %}}

上面代码要求使用至少 Lua 5.1，否则 `luaL_newstate` 需要改成 `lua_open`, `luaL_openlibs` 要拆成单独的各个标准库加载方法比如 `luaopen_io`。

编译需要引用 Lua 头文件并链接 Lua 库，本文所有示例和编译脚本都放在 [这个 Git 仓库](
https://coding.net/u/doitian/p/lua-c-api-intro/git) 中。

Lua C API 的核心就是操作栈，所有的操作都是通过栈实现的。访问栈可以用正数或者负数。每次函数调用会标记当前栈顶的位置，之后压入的元素位置从 1 开始。下面会提到函数的参数会首先压入栈，所以正数 i 引用的栈位置就是第 i 个参数。负数就是从栈顶开始数的位置，-1 就是栈顶元素，-2 就是栈顶下面一个元素，依此类推。

使用栈要注意，谁负责压入就要负责弹出，很多 Lua C API 出现错误都是栈操作不当引起的。

{{% figure src="/images/201702/lua_stack.png" link="/images/201702/lua_stack.png" title="Lua 栈" %}}

查看 C API 的文档主要要查看是不是有参数需要压入栈，执行后是否会从栈顶弹出元素。

以设置全局变量的 API `lua_setglobal` 为例

    void lua_setglobal (lua_State *L, const char *name);
    Pops a value from the stack and sets it as the new value of global name.

执行该方法需要把全局变量的值压入栈，调用成功后会被自动弹出。下面是使用的例子，注释中是等价的 Lua 代码。完整代码点击文件名查看。

{{% codecaption name="globals.c" link="https://coding.net/u/doitian/p/lua-c-api-intro/git/blob/master/globals.c" %}}

~~~ c
// g_int = 10
lua_pushinteger(L, 10);
lua_setglobal(L, "g_int");

// g_int = 3.14
lua_pushnumber(L, (lua_Number)3.14);
lua_setglobal(L, "g_number");

// g_true = true
// g_false = false
lua_pushboolean(L, 1);
lua_setglobal(L, "g_true");
lua_pushboolean(L, 0);
lua_setglobal(L, "g_false");

// g_string = "global set from C API"
lua_pushstring(L, "global set from C API");
lua_setglobal(L, "g_string");

// g_table = { name = "table set from C API" }
lua_newtable(L);
lua_pushstring(L, "table set from C API");
lua_setfield(L, -2, "name");
lua_setglobal(L, "g_table");
~~~

{{% /codecaption %}}

以最复杂的 `g_table` 为例说明栈的变化。

{{% figure src="/images/201702/lua_setglobal.png" link="/images/201702/lua_setglobal.png" title="Lua 栈变化示例" %}}

## Function

### C 中调用 Lua 方法

上面的例子用到了 integer, float, boolean, string, table 等数据类型。Lua 和 C 之间还可以通过函数互调来共享逻辑。

C 中调用 Lua 方法或者其它 C 模块定义的方法可以使用 `lua_call` 或者 `lua_pcall`。

调用的栈约定是一致的，先把要调用的函数入栈，然后按顺序从第 1 个参数开始压入栈，有多个参数的话这个时候栈顶应该是最后一个参数。

然后调用 `lua_call` 或者 `lua_pcall`，需要手动指定参数的个数和要保留的返回结果的个数。和在 Lua 中方法调用相同，指定的个数小于实际返回结果个数的话，多余的被丢弃，指定的个数多于实际个数的话，多出来的赋值 nil。

调用的函数没有出现错误的话，结果是一致的，函数和所有参数被弹出栈，指定数量的返回结果被依次压入栈，也就是最后一个返回结果会在栈底。如果出错了，`lua_call` 行为和 Lua 中直接调用一个方法然后出错一致， `lua_pcall` 会和成功一样把函数和所有参数弹出栈，然后把错误压入栈。而如果最后一个参数不为 0 则会调用对应栈位置的函数来处理错误。

首先定义一个这样的全局 Lua 函数方便演示。

~~~ lua
function identity(...)
  return table.unpack({...})
end
~~~

下面是 `lua_call` 和 `lua_pcall` 的例子。

{{% codecaption name="call-lua-function.c" link="https://coding.net/u/doitian/p/lua-c-api-intro/git/blob/master/call-lua-function.c" %}}

~~~ c
lua_getglobal(L, "identity"); // identity
lua_pushinteger(L, 1); // identity, 1
lua_call(L, 1, 2);
// r1, r2 = identity(1)
// stack: 1, nil
printf(
    "r1, r2 = %d, %s\n",
    (int)lua_tointeger(L, -2),
    lua_isnil(L, -1) ? "nil" : "not nil"
    );
lua_pop(L, 2);

lua_getglobal(L, "identity"); // identity
lua_pushinteger(L, 1); // identity, 1
lua_pushinteger(L, 2); // identity, 1, 2
status = lua_pcall(L, 2, 1, 0);
if (status) {
  fprintf(stderr, "%s", lua_tostring(L, -1));
  lua_pop(L, 1);
} else {
  printf("r1 = %d\n", (int)lua_tointeger(L, -1));
  lua_pop(L, 1);
}
~~~

{{% /codecaption %}}

### Lua C 方法

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


---
title: Hilight Ruby New Hash In Emacs
tags: [emacs, ruby]
date: "2012-01-12"
description: "Emacs ruby mode patch to highlight the new hash syntax."
hljs: true
hljsLanguages: ["lisp"]
---

Not fully tested, let me know if it mess up your buffer.

{{< codecaption name="my-ruby-mode.el" link="https://gist.github.com/doitian/1600148" >}}

~~~ c
(font-lock-add-keywords
 'ruby-mode
 '(("\\(\\b\\sw[_a-zA-Z0-9]*:\\)\\(?:\\s-\\|$\\)" (1 font-lock-constant-face))))
~~~

{{< /codecaption >}}

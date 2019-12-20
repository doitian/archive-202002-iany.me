---
title: "Flatbuffers Compatible Table"
date: 2018-11-02T10:00:36+08:00
tags: [serialization]
draft: false
description: "How various flatbuffers types are compatible when one is used as child in another"
comment: true
share: true
hljs: false
hljsLanguages: []
mathjax: false
---

| parent | table | struct | union | vector | string | enum | scalar |
| ------ | ----- | ------ | ----- | ------ | ------ | ---- | ------ |
| root   | Y     | Y      |       |        |        |      |        |
| table  | Y     | Y      | Y     | Y      | Y      | Y    | Y      |
| struct |       | Y      |       |        |        | Y    | Y      |
| union  | Y     | Y      |       |        |        |      |        |
| vector | Y     | Y      | Y     |        | Y      | Y    | Y      |

If there is a `Y` in row A column B, B can be used as a child of A. If it is
blank, B is not allowed as a child of A.

Parent `root` means which type can be used as a root object.

---

• [the test
schema](https://github.com/doitian/flatbuffers_compatible_table/blob/master/compatible_test.fbs)

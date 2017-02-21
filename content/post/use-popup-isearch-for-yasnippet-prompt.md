---
title: Use Popup isearch For Yasnippet Prompt
tags: [emacs]
date: "2012-03-30"
layout: post
description: "Use popup as a backend of yasnippet prompt"
---

[Yasnippet][] tries functions in `yas/prompt-functions` when it needs user to
select one choice, such as selecting snippets with the same trigger key, such
as helper method `yas/choose-value`.

[popup][] is a visual popup interface library extracted from [auto-complete][]
by its author. It has better look and feel than all the built-in
`yas/prompt-functions`. Also it is easy to customize, and its isearch mode is
very efficient, the items are filtered on-the-fly when typing.

<!--more-->

<figure class="half">
  <img src="/images/201203/choises.png">
  <img src="/images/201203/filter_by_keyword.png">
  <figcaption>
    <h4>Popup snapshop</h4>
  </figcaption>
</figure>

The integration is easy. Load `popup.el`, implement one prompt function and
add it to `yas/prompt-functions`.

{{< gist doitian 2245733 "yasnippet-popup-isearch-prompt.el" >}}

[yasnippet]: http://capitaomorte.github.com/yasnippet/index.html
[popup]: https://github.com/m2ym/popup-el
[auto-complete]: https://github.com/m2ym/auto-complete

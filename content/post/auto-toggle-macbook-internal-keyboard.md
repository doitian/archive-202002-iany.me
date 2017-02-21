---
title: Auto Toggle MacBook Internal Keyboard
tags: [mac, powerTool]
date: "2014-01-17"
image:
  feature: /images/201401/keyboard-on-mac.png
description: "Automate disable/enable internal keyboard when an external keyboard is attached/detacched."
---

I prefer using external keyboard with my MacBook. When no external monitors
are used, a typical setup is placing the keyboard above the internal one, so I
can still use the internal touchpad.

But sometimes the external keyboard may press some keys of the internal
keyboard. There is a
[solution](http://forums.macrumors.com/showthread.php?t=433407) to disable the
internal keyboard, but it is tedious to run the command manually.

    # Disable, ignore the warning
    sudo kextunload /System/Library/Extensions/AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext/
    # Enable
    sudo kextload /System/Library/Extensions/AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext/

Fortunately, [Keyboard Maestro](http://www.keyboardmaestro.com/main/) supports
executing scripts when a USB device is attached or detached.

<!--more-->

I have created two macros to enable and disable
internal keyboard.

Before the macros can be used, you must setup sudoers to allow running the
command without password.

    $ sudo visudo

And append following line to the file and save it.

    %admin ALL = NOPASSWD: /sbin/kextunload /System/Library/Extensions/AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext, /sbin/kextload /System/Library/Extensions/AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext

Then restart sudo session

    $ sudo -K

You can [import the macros]({{ site.cdn }}/files/201401/Internal Keyboard.kmmacros) or create by
yourself. You have to change the USB device name to match your external
keyboard, which can be checked in system information.

{% capture images %}
  {{ site.cdn }}/images/201401/usb-device-name.png
  {{ site.cdn }}/images/201401/enable.png
  {{ site.cdn }}/images/201401/disable.png
{% endcapture %}
{% include gallery images=images caption="Popup snapshot" cols=3 %}

# Webehome integration for Home assistant

This component makes it possible to integrate your webehome devices into
home assistant. 

Supported devices:
- Alarm box (with alarm status, online status, last event and more..)
- Motion detectors (PIR)
- Magnetic contacts


# Setup

Copy the *custom_components* directory in this repo to the root of your
home assistant *config* folder. You might already have a directory named
"custom_component" in there if so, merge the directories.


## Configuration in Home Assistant

```
webehome:
  username: !secret webehome_username
  password: !secret webehome_password
```

If you what you can add a new webehome user to use with this component.
That is done with the webehome app or web gui. The permissions could be a
normal user.

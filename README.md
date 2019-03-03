# Webehome integration for Home assistant

This component makes it possible to integrate your webehome devices into
home assistant. 

Supported devices:
- Alarm box (with alarm status, online status, last event and more..)
- Motion detectors (PIR)
- Magnetic contacts


# Installation

- Clone or copy the root of the repository into `<config 
dir>/custom_components/webehome`

```
cd /path/to/homeassisant
mkdir custom_components
cd custom_components
git clone https://github.com/bratanon/ha-webehome.git webehome
```

## Configuration in Home Assistant

```
webehome:
  username: !secret webehome_username
  password: !secret webehome_password
```

If you what you can add a new webehome user to use with this component.
That is done with the webehome app or web gui. The permissions could be a
normal user.

# Setup

Copy the files in this repo to your home assistant config folder. You might already have a directory named "custom_component" in there, otherwise create it.


## Configuration in Home Assistant

```
webehome:
  username: !secret webehome_username
  password: !secret webehome_password
```

If you what you can add a new webehome user to use with this component.
That is done with the webehome app or web gui. The permissions could be a normal user.

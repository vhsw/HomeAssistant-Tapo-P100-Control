# Home Assistant Tapo P100 Control

A custom integration for Home Assistant to control the Tp-Link Tapo P100 smart plugs

## Installation

To install the Tapo P100 integration copy the `tapo_p100_control` folder into the `custom_components` folder on your home assistant instance then these lines should be added to your `configuration.yaml` file.

```yaml
switch:
  platform: tapo_p100_control
  ip_address: 192.168.x.x
  email: email@gmail.com
  password: Password123
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change

## Upcoming Features

- UI setup integration
- Uploading to HACS

## Contributors

- [K4CZP3R](https://github.com/K4CZP3R)
- [Extreeeme](https://github.com/Extreeeme)
- [vhsw](https://github.com/vhsw)

## License

[MIT](https://choosealicense.com/licenses/mit/)

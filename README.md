# Description

Simple python-script to control ssh-tunnels.

If you use ssh-tunnels, once there may be too many of them. They can fall off. They need to be restarted and so on.
A simple python script runs tunnels in separated processes and periodically pings the ports to which they are routed.
If something is wrong (fell off wi-fi, restarted vpn, etc.) - the tunnel restarts.

Also this script provides a  web-interface for view list of tunnels and start/stop them.

## Usage

To start you need to go to the project directory:

```bash
cd tunnels
```

Edit the configuration file:

```bash
vi config.json
```

The configuration is set in JSON format:

```json
{
    "ui_port": 8001,
    "max_death_count": 5,
    "timeout": 3,
    "tunnels": [{...}]
}
```

where:

- ui_port - web-interface port, default: 8000
- max_death_count - number of falls of the tunnel after which recovery attempts will stopped, default: 5
- timeout - timeout in seconds between tunnel ping, default: 3 sec
- tunnels - list of configurations of the tunnels
- logging_conf - logger configuration

Tunnel configuration:

```json
{
    "name": "Tunnel One name",
    "note": "Monitoring server",
    "cmd": "ssh -N -p 22 10.10.10.10 -L 7676:11.11.11.10:7777",
    "local_port": 7676,
    "url": "http://localhost:7676/",
    "enabled": false
}
```

where:

- name - tunnel name, displayed in the web-interface
- note - tunnel description, displayed in the web interface, may be empty;
- cmd - ssh command for the establish tunnel, note that multiple tunnels can be raised with a single SSH call; 
- local_port - local port on the localhost for ping, for multiple tunnels use any;
- url - URL for the browser, displayed in the web interface, may be empty, or example, it is convenient to throw tunnels to jupyter and be able to immediately open it on the finished link;
- enabled - flag: true - the tunnel is enabled and will start at startup, false - the tunnel is disabled and stopped at startup. It can be run later via the web interface

### Run

Run with a default configuration file:

```bash
python3 tunns.py
```

Run with a custom configuration files:

```bash
python3 tunns.py path_to/config_file.json
```

### Web-interface

Web-interface displayed list of tunnels, status and state of enabled or disabled them;

Open in a browser:

```bash
    http://localhost:[ui_port]
```

where:

- [ui_port] - web-interface port

Default link:

```bash
http://localhost:8000
```

## Requirements

Python>3.2

## Описание

Простой python-скрипт для контроля ssh-туннелей.

Если вы испльзуете ssh-туннели, то в какой-то момент их может стать слишком много. Они могут отваливаться. Их нужно перезапускать и тд.
Простой python-скрипт запускает туннули в отдельных процессах и периодически пингует порты, на которые они проброшены.
Если что-то не так (отвалилися wi-fi, перезапустился vpn и тд) - туннель перезапускается.

Так же скрипт передоставляет веб-интерфейс для управления туннелями - их можно запускать и останаваливать.

## Требования

Python>3.2

## Использование

Для старта или настройки нужно перейти в дирикторию проекта:

```bash
cd tunnels
```

### Настройка

Отредактируйте файл конфигурации:

```bash
vi config.json
```

Конфигурация задается в JSON формате:

```json
{
    "ui_port": 8001,
    "max_death_count": 5,
    "timeout": 3,
    "tunnels": [{...}]
}
```

где:

- ui_port - порт веб-интерфейса, для открытия в браузере: `http://localhost:[ui_port]`, по умолчанию порт 8000
- max_death_count - количество падений туннуля, после которого попытки восстановления прекратятся, поумолчанияю 5 раз
- timeout - задержка в секундах между пингами туннелей, по умолчанию 3 секунды
- tunnels - список конфигурация туннелей, конфигурация туннеля расмотрена ниже
- logging_conf - настройки стнадартного логгера

Конфигурация туннеля:

```json
{
    "name": "Tunnel One name",
    "note": "Monitoring server",
    "cmd": "ssh -N -p 22 10.10.10.10 -L 7676:11.11.11.10:7777",
    "local_port": 7676,
    "url": "http://localhost:7676/",
    "enabled": false
}
```

где:

- name - название туннеля, отображается в веб-интерфейсе
- note - описание туннеля, отображается в веб-интерфейсе, может быть пустым,
- cmd - ssh команда устанавливающая туннель или туннели, обратите внимание, что одним вызовом ssh можно поднять сразу несколько туннелей
- local_port - порт туннеля на локальной машине, если туннелей несколько, можно указать любой
- url - URL в браузере, отображается в веб-интерфейсе, например удобно пробрасывать туннели до jupyter и иметь возможность сразу его открыть по готовой ссылке
- enabled - флажок: true - туннель включен и запустится при старте, false - туннель выключен. Его можно включить позже через веб-интерфейс

Конфигурации туннелей задаются в конфигурационном файле. Файлов конфигурации может быть много, например для разных групп сервисов или для дома/работы, и т.п.

### Запуск

Запуск с файлом конфигурации по умолчанию:

```bash
python3 tunns.py
```

Запуск с заданным файлом конфигурации:

```bash
python3 tunns.py path_to/config_file.json
```

### Веб-интерфейс

Веб-интерфейс отображает список туннелей, их состояние и признак включен/выключен
Для перехода в интрфейс, откроете в браузере ссылку: 

```bash
http://localhost:[ui_port]
```

где:

- [ui_port] - адрес порта на котором запущен интерфейс

Поумолчанию ссылка:

```bash
http://localhost:8000
```

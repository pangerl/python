## 安装pygame

### MAC的坑

- mac安装注意指定版本，`pip install pygame==1.9.2`，不然报错`src/scrap.c:27:10: fatal error: 'SDL.h' file not found`
后来找到原因，pygame最新版本为1.9.3，需要先安装其他组件，`brew install sdl sdl_image sdl_mixer sdl_ttf portmidi mercurial`
这样就可以直接安装pygame最新版了。

- mac上开发，如果使用虚拟环境安装的python，用pygame开发时，程序无法捕捉键盘的输入。也就是说python不能用pyenv，或virtualenv来安装。需要安装到osx的本地环境。因为我是装在pyenv中，所以用键盘输入没有任何反应。查了很多资料，这个问题无解。所以最后游戏测试，我是在Windows上完成的。
网上有一个解决方法，可以试试，虽然在我这报错了。

```
# create a virtualenv called 'anenv' and use it.
python3 -m virtualenv anenv
. ./anenv/bin/activate
# venvdotapp helps the python be a mac 'app'. So the pygame window can get focus.
python -m pip install venvdotapp
venvdotapp
python -m pip install pygame

# See if pygame works with the oo module, and the aliens example.
python -m pygame.examples.aliens
```


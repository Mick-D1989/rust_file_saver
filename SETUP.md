1) Install WSL
Install on Windows Host Machine;
```
wsl --install
```
```
wsl --install Ubuntu-24.04
```

Enter WSL and set-up a user account (follow the prompts to enter username and password);
```
wsl -d Ubuntu-24.04
```
go back to windows host;
```
exit
```
2) Download podman on Windows Host Machine;

```
wget -O podman-5.4.0-setup.exe https://github.com/containers/podman/releases/download/v5.4.0/podman-5.4.0-setup.exe
``` 
And install it (Follow the installer - Install with WSL2)
```
podman-5.4.0-setup.exe
```
Powershell won't recognise the `podman` command until the shell is restarted, so exit and start a new one

Make sure any old versions of podman have been removed correctly;
```
podman machine rm podman-machine-default
```
and 
```
podman machine rm podman-machine-default-root
```

crate a new podman machine;

```
podman machine init
```
and start it (should be configured in rootless mode)
```
podman machine start
```

3) download and configure podman on WSL;
Enter WSL at your /home/\<USERNAME> location
```
wsl ~
```

download the same version binary of podman as you did for the host machine, in this case v5.4.0
```
wget https://github.com/containers/podman/releases/download/v5.4.0/podman-remote-static-linux_amd64.tar.gz
```

extract it to your local folder;
```
sudo tar -C /usr/local -xzf podman-remote-static-linux_amd64.tar.gz
```

add local to path;
```
export PATH="$PATH:/usr/local/bin"
```

rename the binary to `podman` so compose works later on;
```
sudo mv /usr/local/bin/podman-remote-static-linux_amd64 /usr/local/bin/podman
```

add the rootless connection;
```
podman system connection add --default podman-machine-default-root unix:///mnt/wsl/podman-sockets/podman-machine-default/podman-root.sock
```

give access to remote Podman;
```
sudo usermod --append --groups 10 $(whoami)
```
then exit WSL with `exit` and then start a new WSL session

check that `uucp` and whatever your linux username is, both appear in the groups now;
```
groups
```
Verify that Podman default system connections is set to your remote podman machine;
```
podman system connection list
```
Output;
```
Name                         URI                                                                     Identity    Default     ReadWrite
podman-machine-default-user  unix:///mnt/wsl/podman-sockets/podman-machine-default/podman-user.sock              true        true
```
Verify the server is working;
```
podman version
```
Output;
```
Client:       Podman Engine
Version:      5.4.0
API Version:  5.4.0
Go Version:   go1.23.6
Git Commit:   f9f7d48b24b1ca4403f189caaeab1cb8ff4a9aa2
Built:        Wed Feb 12 05:04:19 2025
OS/Arch:      linux/amd64

Server:       Podman Engine
Version:      5.4.0
API Version:  5.4.0
Go Version:   go1.23.5
Built:        Tue Feb 11 11:00:00 2025
OS/Arch:      linux/amd64
```

run a container;
```
podman run quay.io/podman/hello
```
and check the last run container (can check this in both WSL and Windows host to make sure further check that they are working on the same socket);
```
podman ps -a --no-trunc --last 1
```

Output should look like this;
```
michael@michael:/mnt/c/WINDOWS/system32$ podman run quay.io/podman/hello
Trying to pull quay.io/podman/hello:latest...
Getting image source signatures
Copying blob sha256:81df7ff16254ed9756e27c8de9ceb02a9568228fccadbf080f41cc5eb5118a44
Copying config sha256:5dd467fce50b56951185da365b5feee75409968cbab5767b9b59e325fb2ecbc0
Writing manifest to image destination
!... Hello Podman World ...!

         .--"--.
       / -     - \
      / (O)   (O) \
   ~~~| -=(,Y,)=- |
    .---. /`  \   |~~
 ~/  o  o \~~~~.----. ~~
  | =(X)= |~  / (O (O) \
   ~~~~~~~  ~| =(Y_)=-  |
  ~~~~    ~~~|   U      |~~

Project:   https://github.com/containers/podman
Website:   https://podman.io
Desktop:   https://podman-desktop.io
Documents: https://docs.podman.io
YouTube:   https://youtube.com/@Podman
X/Twitter: @Podman_io
Mastodon:  @Podman_io@fosstodon.org
michael@michael:/mnt/c/WINDOWS/system32$ podman ps -a --no-trunc --last 1
CONTAINER ID                                                      IMAGE                        COMMAND                            CREATED         STATUS                     PORTS       NAMES
cd2b1c303e39a07a06c00c2c084ccf18619643dc586b5a8707ece990bd2bd0d4  quay.io/podman/hello:latest  /usr/local/bin/podman_hello_world  31 seconds ago  Exited (0) 32 seconds ago              elated_cannon
```

you can change between rootless and rootfull by switching podman machine and the connection like this;

```
podman machine set --rootful=true
```
```
podman system connection add --default podman-machine-default-root unix:///mnt/wsl/podman-sockets/podman-machine-default/podman-root.sock
```

and back again;

```
podman machine set --rootful=false
```
```
podman system connection add --default podman-machine-default-user unix:///mnt/wsl/podman-sockets/podman-machine-default/podman-user.sock
```

Lastly, Install podman-compose;
```
sudo apt update && sudo apt upgrade -y
```
```
sudo apt install python-pip && pip upgrade pip
```
```
pip3 install https://github.com/containers/podman-compose/archive/main.tar.gz --break-system-packages
```
Move the file to the same spot we put podman before;
```
sudo cp /home/<WSL-USERNAME>/.local/bin/podman-compose /usr/local/bin/
```

Check it's using the right version, if it's not, it may have installed an earlier verison of podman with it
you can probably remove it with;
```
sudo apt remove podman
```

4) Set-up CDI config in podman machine;

Enter a SSH session with the podman machine;
Make sure the following is done with podman machine set as root;
```
podman machine stop
```
```
podman machine set --rootful
```
```
podman machine start
```

```
podman machine ssh
```
Download NVIDIA Container-Toolkit
```
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
tee /etc/yum.repos.d/nvidia-container-toolkit.repo && \
yum install -y nvidia-container-toolkit && \
nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml && \
nvidia-ctk cdi list
```
now exit the podman machine and set it back to rootless;
```
podman machine stop
```
```
podman machine set --rootful=false
```
```
podman machine start
```

Run `nvidia-smi` in a container from your host machine to verify the CDI is working;
```
podman run --rm --device nvidia.com/gpu=all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

if you get an error, try generating a new CDI spec file in the podman machine;
```
nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
```



add these to your local setting file in vscode

```
    "dev.containers.dockerComposePath": "podman-compose",

    "dev.containers.dockerPath": "podman",

    "dev.containers.mountWaylandSocket": false,

    "dev.containers.optimisticallyLaunchDocker": false
```
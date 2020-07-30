#!/usr/bin/env bash
## #################################### ##
## The Installer of                     ##
##      _       _     _    _ _          ##
##     | | __ _| |__ | | _(_) |_        ##
##     | |/ _` | '_ \| |/ / | __|       ##
##     | | (_| | |_) |   <| | |_        ##
##     |_|\__,_|_.__/|_|\_\_|\__|       ##
##                                      ##
## ==================================== ##


# 本地安装labkit, 调用setup_env.sh

# 调试脚本时显示行号
export PS4='+${BASH_SOURCE}:${LINENO}:${FUNCNAME[0]}: '

# 使用未定义变量退出
#set -u

# 出错退出
set -e

function _log() {
    if [ "$_DEBUG" == "true" ]; then
        echo 1>&2 "$@"
    fi
}

function start_echo(){
#    echo -e "\e[32m[➭] \e[0m$@..."
    # echo -e "\e[32m==> \e[0m$@..."
    echo -e "\e[32m==> \e[0m$@"
}



function finish_echo(){
    if [[ $_DEBUG == 'true' ]]; then
        echo -e "\e[36m[✔] \e[0m$@"
    fi
}

function error_echo(){
    echo -e "\e[31m[✘] $@\e[0m"
    exit 1

}


########################
Color_off='\033[0m'       # Text Reset
Black='\033[0;30m'        # Black
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow
Blue='\033[0;34m'         # Blue
Purple='\033[0;35m'       # Purple
Cyan='\033[0;36m'         # Cyan
White='\033[0;37m'        # White

msg() {
    printf '%b\n' "$1" >&2
}

#warn () {
#  msg "${Yellow}[⚠]${Color_off} ${1}${2}"
#}


echo_with_color () {
    printf '%b\n' "$1$2$Color_off" >&2
}

welcome_echo () {
    echo_with_color ${Yellow} "$@"
}


command_exist() {
    command -v "$1" >/dev/null 2>&1
}

welcome () {
    welcome_echo "Installing  "
    welcome_echo "      _       _     _    _ _       "
    welcome_echo "     | | __ _| |__ | | _(_) |_     "
    welcome_echo "     | |/ _\` | '_ \| |/ / | __|    "
    welcome_echo "     | | (_| | |_) |   <| | |_     "
    welcome_echo "     |_|\__,_|_.__/|_|\_\_|\__|    "
    welcome_echo "        "
}

# 获取当前脚本的绝对路径, 也就是labkit的绝对路径
current_dir=$(cd `dirname $0`; pwd)
# cd $current_dir/../
labkit_dir=$(pwd)


function requirement_check {
    # welcome_echo "Labkit requires git installed."
    # if ! command_exist "git"; then
    # error_echo "You must have 'git' installed to continue"
    # fi
    # welcome_echo "Labkit requires beanstalkd installed or require wget and gcc to get and compile it."
    # welcome_echo "You can use yum or apt-get on your system to get them."

    if ! command_exist "beanstalkd"; then
        if ! command_exist "wget"; then
            error_echo "You must have 'wget' installed to continue"
            welcome_echo "You can use yum or apt-get on your system to get it."
        fi
        if ! command_exist "gcc"; then
            error_echo "You must have 'gcc' installed to continue"
            welcome_echo "You can use yum or apt-get on your system to get it."
        fi
    fi

}


function add_line_to_file {
    # 第一个参数一定要用双引号引起来.
    # 用法: add_line_to_file <line> <file>
    # 例如
    # add_line="source `command -v virtualenvwrapper.sh`"
    # add_line_to_file "$add_line" ~/.bashrc

    grep -q -F "$1" $2 || echo "$1" >> $2
}

############## install envfile #############
function install_envfile {
    start_echo "Creating setenv.sh..."
    # 创建 setenv 配置
    cat   <<END >$labkit_dir/setenv.sh
export PATH=$labkit_dir/bin:\$PATH
# 去重 PATH 环境变量
PATH=\$(printf "%s" "\$PATH" | awk -v RS=':' '!a[\$1]++ { if (NR > 1) printf RS; printf \$1 }')
PYTHONPATH=\$(printf "%s" "\$PYTHONPATH" | awk -v RS=':' '!a[\$1]++ { if (NR > 1) printf RS; printf \$1 }')
END
## 可选加载函数
##source \$labkit_dir/setup/setup_functions.sh


    # 添加到 bashrc
    add_line_to_file "# This line is appended by labkit." ~/.bashrc
    add_line="source $labkit_dir/setenv.sh"
    add_line_to_file "$add_line" ~/.bashrc

    finish_echo "Created setenv file in $labkit_dir/setenv.sh"

}

function setenv {
    source $labkit_dir/setenv.sh
}


############## install beanstalkd #############
function install_beanstalkd {
    # 下载安装beanstalkd
    start_echo "Installing dependence..."
    cd /tmp
    wget https://github.com/kr/beanstalkd/archive/v1.10.tar.gz
    tar -zxvf v1.10.tar.gz
    cd beanstalkd-1.10
    make
    mv ./beanstalkd $labkit_dir/bin

    #set +e
    cd ..
    #set -e

    rm -rf v1.10.tar.gz  beanstalkd-1.10

    #set +e
    cd $labkit_dir
    #set -e

    finish_echo "Dependence installed in labkit bin folder."

}

############## install python #############
PY_VERSION=3.7.4
set -e
command_exist() {
    command -v "$1" >/dev/null 2>&1
}
function install_python {
    start_echo "Installing individual Python..."

    if [ -d /Users/lhr/.pyenv/versions/$PY_VERSION ]; then
        echo "Individual Python already installed."
        return
    fi
    # install pyenv
    if ! command_exist "pyenv"; then
        curl https://pyenv.run | bash
        # add these to ~/.bashrc to enable the pyenv command. In this case just run it.
        export PATH="$HOME/.pyenv/bin:$PATH"
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
    fi

    # install specific python version
    pyenv install $PY_VERSION
    finish_echo "Individual Python installed."


}

############## install buildout #############
function install_buildout {
    start_echo "Installing Python based commands... It may take minutes, please wait"

    # 使用此 $PY_VERSION 进行buildout。
    PYTHON=$HOME/.pyenv/versions/$PY_VERSION/bin/python
    if [[ "$_DEBUG" == "true" ]]; then
        $PYTHON ./bootstrap.py #1>/dev/null 2>/dev/null
        bin/buildout #1>/dev/null 2>/dev/null
    else
        $PYTHON ./bootstrap.py 1>/dev/null 2>/dev/null
        bin/buildout 1>/dev/null 2>/dev/null
    fi
    finish_echo "Python based commands installed."

}


############## install sslink #############
sslink(){
    for d in *; do
      if [ -d "$d" ]; then
        # echo $d
        cd "$d"
        sslink
        cd ..
      elif [[ -f "$d" ]]; then
        # echo ln -s \"$(pwd)/$d\" \"$binfolder/\"
        ln -sf "$(pwd)/$d" "$binfolder/"
      fi
    done
}

function install_sslink {
    start_echo "Installing Shell based commands..."
    export binfolder=$(pwd)/bin
    cd sh

    set +e
    sslink
    set -e
    finish_echo "Shell based commands installed."

}

#################################################
##### =============== main ================= ####
#####                      _                 ####
#####      _ __ ___   __ _(_)_ __            ####
#####     | '_ ` _ \ / _` | | '_ \           ####
#####     | | | | | | (_| | | | | |          ####
#####     |_| |_| |_|\__,_|_|_| |_|          ####
#####                                        ####
#################################################


done_echo () {
    echo_with_color ${Cyan} "$@"
}

function done_msg {
    # done_echo ""
    # done_echo "==> All done! Congratulations! ^_^"
    # done_echo "Labkit appended new path to your PATH to your ~/.bashrc, You should reload it by"
    # done_echo "  source ~/.bashrc  or  bash  or  relogin to your shell"
    # done_echo ""
    # done_echo "Labkit uses virtualenv by virtualenvwrapper, You should activate labkit environment with"
    # done_echo "  workon labkit"
    # done_echo "Then, you can use the labkit command"
    # done_echo "  labkit"
    # done_echo "If you are using labkit for the first time, you should make a ~/labkit_global folder to get start"

    # done_echo "  labkit new labkit-global"
    # done_echo ""
    # done_echo "To escape labkit, in labkit environment, run"
    # done_echo "  deactivate"

    done_echo ""
    done_echo "==> All done! Congratulations! ^_^"
    done_echo "Labkit was installed in the \"$labkit_dir\" folder"
    done_echo "Labkit appended new path to your PATH to your ~/.bashrc, you should reload it by"
    done_echo "  source ~/.bashrc  or  relogin to your shell"
    done_echo ""
    done_echo "The labsub, l.sub, ls_sub, ls_insert command will be available."
    done_echo "To remove Labkit, simply delete the ~/.labkit folder."
    done_echo ""

}


function install {
    install_python
    install_buildout
    install_sslink
    if ! command_exist "beanstalkd"; then
      install_beanstalkd
    fi
    install_envfile
    # setenv
    finish_echo "Labkit installation finished."
    done_msg
}

function print_help {
    echo "Usage:"
    echo "  install.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  help            Show help"
    echo "  install         install Labkit"
    echo "  debug           install Labkit with detailed informations."
    echo "  link            refresh link shell commands inside sh folder to project bin."
    echo "  do function     call functions in this install.sh"

}


function main()
{
    cd $labkit_dir
    welcome
    # requirement_check
    # if [ $? != 0 ]; then exit ;fi
    action=$1
    case $action in
        'help')
            print_help
            ;;
        'install')
            install
            ;;
        'debug')
            _DEBUG=true
            install
            ;;
        'link')
            install_sslink
            ;;
        'do')
            $2
            ;;
        *)
            print_help
            ;;
    esac

}
main $*




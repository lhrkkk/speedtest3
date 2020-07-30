#!/bin/sh
set -e

build_name=$(basename $(pwd))
build_folder='build'

lab=210.45.66.91
lab_docs_dir=/var/www/html/docs/
pub=124.165.205.26
pubport=11001
pub_docs_dir=/mnt/snq/docs/

publish_91() {
    mdbook build
    cd $build_folder && tar zcf $build_name.tar.gz $build_name
    scp $build_name.tar.gz $lab:.
    ssh $lab "mv $build_name.tar.gz $lab_docs_dir"
    ssh $lab "cd $lab_docs_dir && tar zxf $build_name.tar.gz"
    echo "doc published on http://210.45.66.91/docs/$build_name"
}

publish_koushare1() {
    scp -P $pubport $build_name.tar.gz root@$pub:.
    # ssh -p $pubport root@$pub ./publish_docs.sh
    ssh -p $pubport root@$pub "mv $build_name.tar.gz $pub_docs_dir"
    ssh -p $pubport root@$pub "cd $pub_docs_dir && tar zxf $build_name.tar.gz"
    echo "doc published on http://docs.snquantum.com/$build_name"
}

publish() {
    publish_91
    publish_koushare1
}


doc() {
    mdbook serve
}


yolo(){
    # git push
    publish
}


function print_help {
    echo "Usage:"
    echo "  setup.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  help            Show help"
    echo "  lab            build and publish doc to lab"
    echo "  snq            build and publish doc to snq"
    echo "  all            build and publish doc to lab and snq"
}


function main()
{
    [ $# == 0 ] && print_help && exit
    action=$1
    case $action in
        'help')
            print_help
            ;;
        'lab')
            publish_91
            ;;
        'snq')
            publish_koushare1
            ;;
        'all')
            publish
            ;;
        *)
            print_help
            ;;
    esac

}
main $*




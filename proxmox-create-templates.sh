#!/bin/bash

function create_template() {
    
    echo "Creating template $2 ($1)"
    qm create $1 --name $2 --ostype l26 
    qm set $1 --net0 virtio,bridge=vmbr0 
    qm set $1 --serial0 socket --vga serial0 
    qm set $1 --memory 2048 --cores 2 --cpu host 
    qm set $1 --scsi0 ${template_storage}:0,import-from="$(pwd)/$3",discard=on
    qm set $1 --boot order=scsi0 --scsihw virtio-scsi-single
    qm set $1 --agent enabled=1,fstrim_cloned_disks=1
    qm set $1 --ide2 ${template_storage}:cloudinit
    qm set $1 --ipconfig0 "ip6=auto,ip=dhcp"
    qm set $1 --sshkeys ${ssh_keyfile}
    qm set $1 --ciuser ${username}
    qm disk resize $1 scsi0 8G
    qm template $1
    rm $3

}

export ssh_keyfile=$PWD/authorized_keys
export username=serveradmin

if [[ $HOSTNAME == "titan" ]]; then
    export template_storage=vm-storage
    export template_vmids=("3000" "3001")
elif [[ $HOSTNAME == "hive" ]]; then
    export template_storage=local-lvm
    export template_vmids=("2000" "2001")
elif [[ $HOSTNAME == "nano" ]]; then
    export template_storage=local-lvm
    export template_vmids=("1000" "1001")
fi

declare -A disk_images
disk_images["alma9.1"]="${template_vmids[0]}|https://repo.almalinux.org/almalinux/9.1/cloud/x86_64/images/AlmaLinux-9-GenericCloud-latest.x86_64.qcow2"
disk_images["alma8.7"]="${template_vmids[1]}|https://repo.almalinux.org/almalinux/8.7/cloud/x86_64/images/AlmaLinux-8-GenericCloud-latest.x86_64.qcow2"

## Fetch SSH keys
echo "Downloading authorized keys.. "
wget -q --show-progress https://raw.githubusercontent.com/fredrikscode/sshkeys/main/authorized_keys

for name in "${!disk_images[@]}"
do
    value="${disk_images[$name]}"
    IFS="|" read -ra values <<< "$value"
    vmid="${values[0]}"
    url="${values[1]}"

    echo "Downloading disk image.. "
    wget -q --show-progress $url
    create_template $vmid $name $(basename -- $url)
done

rm $ssh_keyfile

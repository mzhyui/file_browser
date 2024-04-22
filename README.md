# file_browser

# Object Storage
> https://github.com/s3fs-fuse/s3fs-fuse

install s3fs

config

`echo ACCESS_KEY_ID:SECRET_ACCESS_KEY > ${HOME}/.passwd-s3fs`

s3-like obs instance:
```bash
s3fs mybucket /path/to/mountpoint fuse.s3fs _netdev,allow_other,use_path_request_style,url=https://url.to.s3/ 0 0
```
or
```bash
echo 'mybucket /path/to/mountpoint fuse.s3fs _netdev,allow_other,use_path_request_style,url=https://url.to.s3/ 0 0' >> /etc/fstab
mount -a
```
the `mybucket` is the bucket name of obs

unmount
```
fusermount -u /path/to/mountpoint
```

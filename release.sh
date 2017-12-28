#!/bin/bash

s3_bucket="angelstats"

set -e

rm -fR ./build/*

set -x

./build.sh

date_str=`date +%Y-%m-%d-%H%M`

dist_dir="./build/${date_str}"

echo "Creating dist ${dist_dir}"
mkdir ${dist_dir}

set +x

mv ./build/*.html ${dist_dir}/
mv ./build/*.css ${dist_dir}/
mv ./build/*.js ${dist_dir}/

set -x

dist_files=$dist_dir/*

aws s3 cp "${dist_dir}/" "s3://${s3_bucket}/${date_str}/" --recursive

echo "All files copied, please make them public now"

#for f in $dist_files
#do
#    filename=$(basename $f)
#    s3_key="${date_str}/${filename}"
#    aws s3 cp "${dist_dir}/${filename}" "s3://${s3_bucket}/${s3_key}"
#    aws s3api put-object-acl --acl public-read --bucket ${s3_bucket} --key ${s3_key}
#done

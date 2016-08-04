from lxml import etree

root = etree.Element('configuration')
test = "-Dmapred.job.queue.name=yamp_medium -Dmapred.compress.map.output=true -Dmapreduce.map.output.compress.codec=org.apache.hadoop.io.compress.SnappyCodec -Dmapreduce.job.split.metainfo.maxsize=-1 -Dmapreduce.job.queuename=yamp_medium -Dmapreduce.job.acl-view-job=* -Dfs.permissions.umask-mode=022 -Dmapreduce.map.memory.mb=4548 -Dmapreduce.map.java.opts=-Xmx2500m -Dmapreduce.reduce.memory.mb=7168 -Dmapreduce.map.java.opts=-Xmx6056m"
for config in test.split("-D"):
    if config:
        keyValue = config.strip().split("=")
        prop = etree.Element("property")
        name = etree.Element("name")
        name.text = keyValue[0]
        value = etree.Element('value')
        value.text = keyValue[1]
        prop.append(name)
        prop.append(value)
        root.append(prop)

s = etree.tostring(root, pretty_print=True)
print s

from properties import TextVectorProperty


tv = TextVectorProperty(device='ZWO ASI120MC-S #0', name='CCD_LOCAL_MODE')
tv.add_item('DIR', '/home/njvh/')
tv.add_item('PREFIX', 'IMAGE_XXX')
print(tv)

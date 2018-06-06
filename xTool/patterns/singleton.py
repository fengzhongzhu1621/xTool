# coding: utf-8
'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


class Singleton(type):
    """Singleton metaclass. Use by defining the metaclass of a class Singleton,
       e.g.: class ThereCanBeOnlyOne:
                  __metaclass__ = Singleton
       在Python 2里，你可以通过在类的声明中定义metaclass
       参数，或者定义一个特殊的类级别的(class-level)__metaclass__属性，来创建元类。在
       Python 3里，__metaclass__属性已经被取消了。

       单件元类

       instance = Singleton(class_name): 创建类class_name的一个实例
    """
    def __call__(class_, *args, **kwargs):
        # 在对象创建时直接返回__call__的内容，使用该方法可以模拟静态方法。
        # 如果实例不存在，则创建实例
        # 如果实例存在，则直接返回以前创建的实例
        if not class_.hasInstance(): # 判断类class_是否存在实例
            # pylint: disable-msg=W0201
            # 创建一个类名为class_的类的实例
            # 如果类class_没有实例，则创建一个实例
            class_.instance = super(Singleton, class_).__call__(*args, **kwargs)
        # 返回创建的类的实例
        return class_.instance

    def deleteInstance(class_):
        ''' Delete the (only) instance. This method is mainly for unittests so
            they can start with a clean slate. 
            删除实例，如果实例存在
        '''
        if class_.hasInstance():
            del class_.instance

    def hasInstance(class_):
        ''' Has the (only) instance been created already? 
            判断实例是否存在
        '''
        return hasattr(class_, 'instance')

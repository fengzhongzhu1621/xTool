"""
访问者模式是一种设计模式，允许你在不修改对象结构的前提下定义作用于这些元素的新操作。
这种模式特别适用于对象结构中的元素类型固定但操作可能频繁变化的情况。
通过访问者模式，你可以将作用于对象结构中的各元素的操作集中到一个或多个访问者对象中，从而实现操作的动态扩展。
是对象访问的一种设计模式，我们可以在不改变要访问对象的前提下，对访问对象的操作做拓展。
访问者模式能把处理方法从数据结构中分离出来，并可以根据需要增加新的处理方法，且不用修改原来的程序代码与数据结构，这提高了程序的扩展性和灵活性。

应用场景
1. 对象结构比较稳定，但经常需要在此对象结构上定义新的操作。
2. 需要对一个对象结构中的对象进行很多不同的并且不相关的操作，而需要避免这些操作“污染”这些对象的类，也不希望在增加新操作时修改这些类。
3. 电商网站的商品分类与操作
4. 图形编辑器的操作处理
5. 编译器和解释器设计

角色
1. Visitor
定义了对每个 Element 访问的行为，它的参数就是被访问的元素，它的方法个数理论上与元素的个数是一样的
因此，访问者模式要求元素的类型要稳定，如果经常添加、移除元素类，必然会导致频繁地修改 Visitor 接口，如果出现这种情况，则说明不适合使用访问者模式。

2. Element
定义了一个接受访问者（accept）的方法，其意义是指每一个元素都要可以被访问者访问。

优点
1. 各角色职责分离，符合单一职责原则
2. 具有优秀的扩展性
3. 使得数据结构和作用于结构上的操作解耦，使得操作集合可以独立变化

缺点
1. 具体元素变更时导致修改成本大, 多个访问者都要修改。
2. 访问者模式的缺点是添加新的顶层元素类型会非常麻烦（几乎所有角色都需要相应改动），它的作用就是牺牲添加顶层元素的灵活性，来换取其余各个角色的独立演化能力。
"""

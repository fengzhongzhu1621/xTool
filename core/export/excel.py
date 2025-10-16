from io import BytesIO

from django.http import StreamingHttpResponse
from django.http.response import HttpResponse
from django.utils.encoding import escape_uri_path
from openpyxl import Workbook

__all__ = [
    "export_to_excel",
    "stream_large_export",
]


def save_virtual_workbook(wb: Workbook) -> bytes:
    """
    将 openpyxl 的 Workbook 对象保存为内存中的二进制数据。

    :param wb: openpyxl 的 Workbook 对象
    :return: 包含 Excel 文件数据的字节串
    """
    # 创建一个 BytesIO 对象，用于在内存中保存Excel文件
    # 临时存储 Workbook 对象的数据，以便后续将其作为 HTTP 响应发送给客户端，而无需先将文件保存到磁盘。
    virtual_workbook = BytesIO()

    # 将 Workbook 保存到 BytesIO 对象
    wb.save(virtual_workbook)

    # 当你调用 wb.save(virtual_workbook) 后，virtual_workbook 的指针位于流的末尾。
    # 如果不重置指针，任何尝试读取 virtual_workbook 的操作（例如通过 getvalue() 或传递给 HttpResponse）都会失败或返回空数据，
    # 因为指针已经在流的末尾，没有数据可读。
    #
    # 将指针重置到开始位置，以便后续读取
    virtual_workbook.seek(0)

    # 获取字节数据
    workbook_bytes = virtual_workbook.getvalue()

    # 关闭 BytesIO 对象（可选，因为 getvalue() 已经读取了所有数据）
    # BytesIO 对象在调用 getvalue() 后不需要显式关闭，因为 getvalue() 会读取所有数据并返回字节串。
    # 不过，为了代码的整洁和资源管理，关闭 BytesIO 是一个好习惯。
    virtual_workbook.close()

    return workbook_bytes


def export_to_excel(wb: Workbook, excel_name: str) -> HttpResponse:
    """
    - 返回excel文件的HttpResponse
    :param wb: excel的Workbook
    :param excel_name: excel文件名
    """

    # 创建 HttpResponse 对象，使用 getvalue() 获取字节数据
    # 设置响应的内容类型为 .xlsx 文件的 MIME 类型，确保浏览器正确识别并处理文件。
    response = HttpResponse(
        content=save_virtual_workbook(wb),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # 设置 Content-Disposition 头部，使浏览器下载文件
    # 使用 filename* 以支持非ASCII字符的文件名
    # 对文件名进行 URL 编码，确保特殊字符不会破坏 HTTP 头部
    response["Content-Disposition"] = f"attachment;filename={escape_uri_path(excel_name)}"

    # 可选：设置 Access-Control-Expose-Headers，允许跨域请求中暴露 Content-Disposition 头部
    # 使得前端 JavaScript 可以读取该头部信息（例如，获取下载的文件名）
    # 强制浏览器下载文件而非直接打开
    response["Access-Control-Expose-Headers"] = "content-disposition"

    return response


# 对于超大文件（>100MB）的进一步优化
def stream_large_export(workbook: Workbook) -> StreamingHttpResponse:
    def file_iterator():
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        while chunk := buffer.read(8192):  # 分块读取
            yield chunk
        buffer.close()

    return StreamingHttpResponse(
        file_iterator(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

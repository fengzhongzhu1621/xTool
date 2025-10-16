from typing import List

from xTool.misc import get_run_command_result, run_command, tou


def list_container_names(pod_name: str, namespace: str) -> List[str]:
    """根据pod名获得容器名 ."""
    cmd = "kubectl get pods -n {} | grep {}".format(namespace, pod_name)
    _, std_out_data, _ = get_run_command_result(cmd)
    std_rows = tou(std_out_data).strip().split("\n")
    container_name_list = []
    for row in std_rows:
        container_name = row.split(" ")[0].strip()
        container_name_list.append(container_name)

    return container_name_list


def run_kubectl_exec_bash(cmd: str, container_name: str, namespace: str):
    """运行容器上的命令 ."""
    cmd = f"kubectl -n {namespace} exec -it {container_name} -- {cmd}"
    run_command(cmd)


def logrotate_nginx_log(pod_name: str, namespace: str, nginx_start_cmd: str):
    """分隔nginx日志 ."""
    # 获得网关的容器列表
    container_name_list = list_container_names(pod_name, namespace)
    for container_name in container_name_list:
        # 添加nginx分隔日志配置
        cmd = (
            """cat>/etc/logrotate.d/nginx<<EOF
        /data/home/user00/logs/nginx/*.log {
            daily
            rotate 30
            copytruncate
            notifempty
            sharedscripts
            postrotate {}
            endscript
        }
        """
            % nginx_start_cmd
        )
        run_kubectl_exec_bash(cmd, container_name, namespace)
        # 执行nginx日志分隔
        cmd = "/usr/sbin/logrotate -f /etc/logrotate.d/nginx"
        run_kubectl_exec_bash(cmd, container_name, namespace)

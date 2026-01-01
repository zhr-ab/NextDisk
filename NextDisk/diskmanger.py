import psutil
import platform
from typing import List, Dict, Any

def get_disk_info() -> Dict[str, Any]:
    system_info = {
        "platform": platform.platform(),
        "system": platform.system(),
        "disks": []
    }
    
    for partition in psutil.disk_partitions():
        disk_info = {
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "fstype": partition.fstype or "UNKNOWN",
            "options": partition.opts
        }
        
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.update({
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "percent": usage.percent,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2)
            })
        except (PermissionError, OSError) as e:
            disk_info["error"] = f"权限不足: {e}"
        except Exception as e:
            disk_info["error"] = f"读取错误: {e}"
        
        system_info["disks"].append(disk_info)
    
    return system_info
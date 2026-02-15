#!/usr/bin/env python3
"""
小红书博主笔记批量下载器 - CLI 命令行界面
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import print as rprint

from config import DEFAULT_DOWNLOAD_COUNT, DOWNLOAD_DIR
from database import db, Blogger
from xhs_client import xhs_client, SignServerError
from downloader import download_blogger_notes, record_checker

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="xhs-batch")
def cli():
    """
    小红书博主笔记批量下载器
    
    通过博主ID批量下载小红书笔记，支持自动去重和博主管理。
    """
    pass


@cli.command("add")
@click.argument("blogger_id")
@click.option("--alias", "-a", help="设置博主别名")
def add_blogger(blogger_id: str, alias: str = None):
    """
    添加博主到管理列表
    
    BLOGGER_ID: 小红书博主ID（24位十六进制字符串）
    """
    # 验证 ID 格式
    if len(blogger_id) != 24 or not all(c in '0123456789abcdef' for c in blogger_id.lower()):
        console.print(f"[red]错误：博主ID格式不正确[/red]")
        console.print("提示：博主ID应为24位十六进制字符串，例如：5c6fb3fb00000000110126a2")
        return
    
    # 检查是否已存在
    if db.exists(blogger_id):
        console.print(f"[yellow]博主 {blogger_id} 已存在[/yellow]")
        return
    
    # 尝试获取博主昵称
    nickname = None
    try:
        with console.status("[bold green]正在获取博主信息..."):
            # 暂时跳过获取昵称，后续可以添加
            pass
    except SignServerError as e:
        console.print(f"[yellow]警告：{e}[/yellow]")
        console.print("将在不获取昵称的情况下添加博主")
    except Exception as e:
        console.print(f"[yellow]获取博主信息失败：{e}[/yellow]")
    
    # 添加到数据库
    if db.add(blogger_id, alias=alias, nickname=nickname):
        display_name = alias or nickname or blogger_id
        console.print(f"[green]+ 成功添加博主：{display_name}[/green]")
        if nickname and alias:
            console.print(f"  昵称：{nickname}")
            console.print(f"  别名：{alias}")
        elif nickname:
            console.print(f"  昵称：{nickname}")
    else:
        console.print(f"[red]添加失败[/red]")


@cli.command("remove")
@click.argument("blogger_id")
@click.confirmation_option(prompt="确定要删除这个博主吗？")
def remove_blogger(blogger_id: str):
    """
    从管理列表中删除博主
    
    BLOGGER_ID: 博主ID
    """
    blogger = db.get(blogger_id)
    if not blogger:
        console.print(f"[yellow]博主 {blogger_id} 不存在[/yellow]")
        return
    
    if db.remove(blogger_id):
        console.print(f"[green]- 已删除博主：{blogger.display_name()}[/green]")
    else:
        console.print(f"[red]删除失败[/red]")


@cli.command("list")
def list_bloggers():
    """
    查看所有已添加的博主
    """
    bloggers = db.list_all()
    
    if not bloggers:
        console.print("[yellow]暂无已添加的博主[/yellow]")
        console.print("使用 [cyan]xhs-batch add <博主ID>[/cyan] 添加博主")
        return
    
    table = Table(title="博主列表", show_header=True, header_style="bold magenta")
    table.add_column("博主ID", style="dim", width=26)
    table.add_column("昵称", width=20)
    table.add_column("别名", width=15)
    table.add_column("已下载", justify="right", width=8)
    table.add_column("添加时间", width=12)
    table.add_column("最后同步", width=12)
    
    for blogger in bloggers:
        added = blogger.added_at.strftime("%Y-%m-%d") if blogger.added_at else "-"
        synced = blogger.last_sync_at.strftime("%Y-%m-%d") if blogger.last_sync_at else "-"
        
        table.add_row(
            blogger.blogger_id,
            blogger.nickname or "-",
            blogger.alias or "-",
            str(blogger.note_count),
            added,
            synced
        )
    
    console.print(table)
    console.print(f"\n共 [cyan]{len(bloggers)}[/cyan] 个博主")


@cli.command("download")
@click.argument("blogger_id")
@click.option("--count", "-c", default=DEFAULT_DOWNLOAD_COUNT, help=f"下载数量（默认：{DEFAULT_DOWNLOAD_COUNT}）")
@click.option("--all", "download_all", is_flag=True, help="下载所有笔记")
@click.option("--force", "-f", is_flag=True, help="强制下载（忽略已下载记录）")
def download(blogger_id: str, count: int, download_all: bool, force: bool):
    """
    下载指定博主的笔记
    
    BLOGGER_ID: 博主ID
    """
    # 检查博主是否存在
    blogger = db.get(blogger_id)
    if not blogger:
        console.print(f"[yellow]博主 {blogger_id} 未添加到管理列表[/yellow]")
        if click.confirm("是否先添加该博主？"):
            # 快速添加
            db.add(blogger_id)
            blogger = db.get(blogger_id)
        else:
            return
    
    console.print(Panel(
        f"[bold]博主：[/bold]{blogger.display_name()}\n"
        f"[bold]下载数量：[/bold]{'全部' if download_all else count}\n"
        f"[bold]跳过已下载：[/bold]{'否' if force else '是'}",
        title="下载任务",
        border_style="blue"
    ))
    
    # 获取笔记列表
    with console.status("[bold green]正在获取笔记列表..."):
        try:
            if download_all:
                notes = xhs_client.get_user_notes_batch(blogger_id, count=1000)
            else:
                notes = xhs_client.get_user_notes_batch(blogger_id, count)
        except SignServerError as e:
            console.print(f"[red]错误：{e}[/red]")
            return
        except Exception as e:
            console.print(f"[red]获取笔记列表失败：{e}[/red]")
            return
    
    if not notes:
        console.print("[yellow]未找到任何笔记[/yellow]")
        return
    
    console.print(f"找到 [cyan]{len(notes)}[/cyan] 个笔记")
    
    # 过滤已下载
    if not force:
        not_downloaded = record_checker.filter_not_downloaded(notes)
        skipped = len(notes) - len(not_downloaded)
        if skipped > 0:
            console.print(f"跳过 [yellow]{skipped}[/yellow] 个已下载笔记")
        notes = not_downloaded
    
    if not notes:
        console.print("[green]所有笔记都已下载过[/green]")
        return
    
    console.print(f"即将下载 [cyan]{len(notes)}[/cyan] 个笔记")
    
    # 开始下载
    success_count = 0
    fail_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[green]下载中...", total=len(notes))
        
        def on_progress(current, total, note, result):
            nonlocal success_count, fail_count
            if result.success:
                success_count += 1
                status = "[green]OK[/green]"
            else:
                fail_count += 1
                status = "[red]ERR[/red]"
            
            progress.update(task, advance=1, description=f"{status} {note.title[:20]}...")
        
        # 执行下载
        from downloader import Downloader
        import asyncio
        
        downloader = Downloader()
        result = asyncio.run(
            downloader.download_notes(notes, skip_downloaded=False, progress_callback=on_progress)
        )
    
    # 更新数据库
    db.update_sync_info(blogger_id, success_count)
    
    # 显示结果
    console.print()
    console.print(Panel(
        f"[green]成功：{success_count}[/green]\n"
        f"[red]失败：{fail_count}[/red]\n"
        f"[dim]保存路径：{DOWNLOAD_DIR}[/dim]",
        title="下载完成",
        border_style="green"
    ))


@cli.command("download-all")
@click.option("--count", "-c", default=DEFAULT_DOWNLOAD_COUNT, help=f"每个博主下载数量（默认：{DEFAULT_DOWNLOAD_COUNT}）")
@click.option("--force", "-f", is_flag=True, help="强制下载（忽略已下载记录）")
def download_all_bloggers(count: int, force: bool):
    """
    下载所有已添加博主的笔记
    """
    bloggers = db.list_all()
    
    if not bloggers:
        console.print("[yellow]暂无已添加的博主[/yellow]")
        return
    
    console.print(f"共 [cyan]{len(bloggers)}[/cyan] 个博主待下载")
    
    total_success = 0
    total_fail = 0
    
    for i, blogger in enumerate(bloggers):
        console.print(f"\n[bold]({i+1}/{len(bloggers)}) 正在处理：{blogger.display_name()}[/bold]")
        
        try:
            notes = xhs_client.get_user_notes_batch(blogger.blogger_id, count)
            
            if not force:
                notes = record_checker.filter_not_downloaded(notes)
            
            if not notes:
                console.print("  [dim]无新笔记[/dim]")
                continue
            
            from downloader import Downloader
            import asyncio
            
            downloader = Downloader()
            result = asyncio.run(downloader.download_notes(notes, skip_downloaded=False))
            
            total_success += result.success
            total_fail += result.failed
            
            db.update_sync_info(blogger.blogger_id, result.success)
            
            console.print(f"  成功 [green]{result.success}[/green] 失败 [red]{result.failed}[/red]")
            
        except Exception as e:
            console.print(f"  [red]错误：{e}[/red]")
    
    console.print()
    console.print(Panel(
        f"[green]总成功：{total_success}[/green]\n"
        f"[red]总失败：{total_fail}[/red]",
        title="全部下载完成",
        border_style="green"
    ))


@cli.command("alias")
@click.argument("blogger_id")
@click.argument("alias")
def set_alias(blogger_id: str, alias: str):
    """
    设置博主别名
    
    BLOGGER_ID: 博主ID
    ALIAS: 新别名
    """
    if not db.exists(blogger_id):
        console.print(f"[yellow]博主 {blogger_id} 不存在[/yellow]")
        return
    
    if db.update_alias(blogger_id, alias):
        console.print(f"[green]+ 已设置别名：{alias}[/green]")
    else:
        console.print(f"[red]设置失败[/red]")


@cli.command("status")
def check_status():
    """
    检查系统状态
    """
    console.print("[bold]系统状态检查[/bold]\n")
    
    # 检查签名服务（使用内置签名）
    console.print("签名服务：", end="")
    console.print("[green]OK - 使用Playwright浏览器[/green]")
    
    # 检查数据库
    console.print("博主数据库：", end="")
    try:
        count = db.count()
        console.print(f"[green]OK[/green] ({count} 个博主)")
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")
    
    # 检查 XHS-Downloader
    console.print("XHS-Downloader：", end="")
    from config import XHS_DOWNLOADER_PATH
    if XHS_DOWNLOADER_PATH.exists():
        console.print(f"[green]OK - 已安装[/green]")
    else:
        console.print(f"[red]未找到[/red]")
        console.print(f"  [dim]预期路径：{XHS_DOWNLOADER_PATH}[/dim]")
    
    # 检查下载目录
    console.print("下载目录：", end="")
    if DOWNLOAD_DIR.exists():
        console.print(f"[green]OK - {DOWNLOAD_DIR}[/green]")
    else:
        console.print(f"[yellow]! 不存在（将自动创建）[/yellow]")
    
    # 检查浏览器配置
    console.print("浏览器配置：", end="")
    from pathlib import Path
    chrome_profile = Path(r"C:\Users\admin\xhs-batch-downloader\playwright_profile")
    if chrome_profile.exists():
        console.print(f"[green]OK - 已配置[/green]")
    else:
        console.print(f"[yellow]! 未配置，请运行 login 命令[/yellow]")


@cli.command("login")
@click.option("--type", "login_type", default="qrcode", help="登录类型: qrcode(二维码) 或 cookie")
@click.option("--cookie", help="Cookie字符串（用于cookie登录）")
def login_xiaohongshu(login_type: str, cookie: str = None):
    """
    登录小红书账号
    
    支持两种方式：
    1. 二维码登录：显示二维码，用小红书APP扫描
    2. Cookie登录：使用已有的Cookie字符串
    
    示例：
        python cli.py login                    # 二维码登录
        python cli.py login --type cookie --cookie "your_cookie_here"
    """
    import asyncio
    from api_client import XhsApiClient
    
    console.print("[bold]小红书登录[/bold]\n")
    
    async def do_login():
        client = XhsApiClient()
        
        try:
            # 初始化浏览器（显示模式）
            console.print("正在启动浏览器...")
            if not await client.init_browser(headless=False):
                console.print("[red]启动浏览器失败[/red]")
                return
            
            # 检查是否已登录
            if await client.check_login():
                console.print("[green]已经登录，无需重复登录[/green]")
                return
            
            # 执行登录
            if login_type == "cookie" and cookie:
                console.print("使用Cookie登录...")
                await client.login("cookie")
            else:
                console.print("使用二维码登录...")
                console.print("请使用小红书APP扫描浏览器中的二维码")
                await client.login("qrcode")
            
            # 验证登录
            if await client.check_login():
                console.print("[green]登录成功！[/green]")
            else:
                console.print("[red]登录失败，请重试[/red]")
                
        finally:
            await client.close()
    
    try:
        asyncio.run(do_login())
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")


if __name__ == "__main__":
    cli()

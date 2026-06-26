"""独立脚本 — 测试 MongoDB Atlas 数据库连接。"""
import asyncio
import sys
import os
import io

# 修复 Windows GBK 编码问题 — 强制 stdout/stderr 使用 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 确保 server 目录在 path 中
sys.path.insert(0, os.path.dirname(__file__))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def test_connection():
    mongo_url = os.getenv("MONGODB_URL", "")
    if not mongo_url:
        print("❌ MONGODB_URL 未设置，请检查 .env 文件")
        return False

    # 隐藏密码后打印
    masked = mongo_url[: mongo_url.index("@")] if "@" in mongo_url else mongo_url
    masked = masked[: masked.index(":") + 3] + "***" + masked[masked.index("@") :] if "@" in masked else masked
    print(f"连接串: {masked}")

    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=10000)
        # ping 测试
        await client.admin.command("ping")
        print("✅ MongoDB Atlas 连接成功！")

        # 获取数据库信息
        db = client.get_default_database()
        print(f"默认数据库: {db.name}")

        # 列出集合
        cols = await db.list_collection_names()
        print(f"现有集合 ({len(cols)}): {cols if cols else '(空 — 首次写入时会自动创建)'}")

        # 测试写入
        test_col = db["_connection_test"]
        result = await test_col.insert_one({"test": "ok", "timestamp": __import__("datetime").datetime.now().isoformat()})
        print(f"✅ 写入测试成功 (doc id: {result.inserted_id})")

        # 测试读取
        doc = await test_col.find_one({"_id": result.inserted_id})
        print(f"✅ 读取测试成功: {doc}")

        # 清理
        await test_col.delete_one({"_id": result.inserted_id})
        await test_col.drop()
        print("✅ 清理完成")

        print("\n🎉 数据库连接完全正常！")
        return True

    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

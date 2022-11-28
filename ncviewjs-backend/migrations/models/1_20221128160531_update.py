from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "store" ADD "protocol" VARCHAR(255) NOT NULL;
        ALTER TABLE "store" ADD "md5_id" VARCHAR(255) NOT NULL;
        ALTER TABLE "store" ADD "key" VARCHAR(255) NOT NULL;
        ALTER TABLE "store" ADD "bucket" VARCHAR(255) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "store" DROP COLUMN "protocol";
        ALTER TABLE "store" DROP COLUMN "md5_id";
        ALTER TABLE "store" DROP COLUMN "key";
        ALTER TABLE "store" DROP COLUMN "bucket";"""

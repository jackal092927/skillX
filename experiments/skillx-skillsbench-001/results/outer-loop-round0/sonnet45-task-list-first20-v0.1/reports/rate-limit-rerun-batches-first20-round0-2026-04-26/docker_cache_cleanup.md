# Docker Cache Cleanup Notes

- cleanup_time: `2026-04-26`
- action: `docker image prune -f`
- dangling_images_before: `23`
- dangling_images_after: `0`
- BuildKit build cache was intentionally kept for rerun speed.
- No SkillX/Harbor containers were running during cleanup; only unrelated `multica-*` containers were active.

## Current Docker Space Summary

```text
TYPE=Images TOTAL=4 ACTIVE=3 SIZE=988.6MB RECLAIMABLE=228MB (23%)
TYPE=Containers TOTAL=3 ACTIVE=3 SIZE=63B RECLAIMABLE=0B (0%)
TYPE=Local Volumes TOTAL=2 ACTIVE=2 SIZE=50.62MB RECLAIMABLE=0B (0%)
TYPE=Build Cache TOTAL=2224 ACTIVE=0 SIZE=31.49GB RECLAIMABLE=31.37GB
```

## Remaining Named Images

```text
multica-web	dev	7b5ec4cc4491	249MB
multica-backend	dev	2ec0893b5500	48.5MB
golang	1.26-alpine	4e1ae4813de3	237MB
pgvector/pgvector	pg17	076f69e404b7	463MB
```

## Removed Dangling Images Inventory

These images had no repository/tag and no running containers. They are stale final/intermediate image records, not the BuildKit cache needed for fast reruns.

```text
34ac3b47f1df	18 hours ago	2.39GB
1fc3137328d9	18 hours ago	150MB
6422acb77179	18 hours ago	150MB
79021eb21720	18 hours ago	150MB
fe0038f6f606	18 hours ago	150MB
1b355001c33e	18 hours ago	150MB
24797a4f45ec	18 hours ago	150MB
609634feba4e	19 hours ago	150MB
56d233cdedee	19 hours ago	150MB
334c3b4a1df5	22 hours ago	2.08GB
40c2026837b3	23 hours ago	2.08GB
80d5126c41f6	23 hours ago	2.08GB
f5b72ae9a9b5	23 hours ago	2.08GB
8a4bf73fd316	23 hours ago	2.08GB
846869311c6b	24 hours ago	2.14GB
ba789281108b	24 hours ago	2.14GB
58500d337285	25 hours ago	2.14GB
d5e441d4479d	27 hours ago	704MB
a9d5b5c6d3f5	29 hours ago	2.41GB
d6d39602ef2a	30 hours ago	512MB
ee8479d7df9a	32 hours ago	511MB
577bdbc9819d	34 hours ago	5.66GB
598758357895	35 hours ago	2.39GB
```

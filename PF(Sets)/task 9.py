s1={1,2,3}
s2={3,4,5}
s3={7,8,9}
s2.update(s3)
s1.update(s2)
print(s1)
print(s2)
print(s3)
print(set.intersection(s1,s2))
s1.intersection_update(s2)
s2.intersection_update(s3)
print(s1)
print(s2)
print(s3)
print(s2.isdisjoint(s3))
print(s1.issubset(s2))

print(s1.symmetric_difference(s2))
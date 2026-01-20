import mongoose from "mongoose";
import { useVirtualId } from "../db/database.mjs";

// versionKey : mongoose가 문서를 저장할 때 자동으로 추가하는 _v라는 필드를 설정
const userSchema = new mongoose.Schema(
  {
    userid: { type: String, require: true },
    name: { type: String, require: true },
    email: { type: String, require: true },
    password: { type: String, require: true },
    url: String,
  },
  { versionKey: false }
);

// 이거 통과하면 아이디 하나 더 생긴다
useVirtualId(userSchema);
const User = mongoose.model("User", userSchema); // 컬렉션 이름을 정해줌. 항상 단수로 쓴다.

export async function createUser(user) {
  return new User(user).save().then((data) => data.id);
}

export async function loginUser(userid, password) {
  const user = users.find(
    (user) => user.userid === userid && user.password === password
  );
  return user;
}

export async function findByUserid(userid) {
  return User.findOne({ userid });
}

export async function findById(id) {
  return User.findById(id);
}

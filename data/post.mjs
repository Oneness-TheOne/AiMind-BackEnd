import mongoose from "mongoose";
import { useVirtualId } from "../db/database.mjs";
import * as UserRepository from "./auth.mjs";

const postSchema = new mongoose.Schema(
  {
    text: { type: String, require: true },
    userIdx: { type: String, require: true },
    name: { type: String, require: true },
    userid: { type: String, require: true },
    url: String,
  },
  { timestamps: true }
);

useVirtualId(postSchema);
const Post = mongoose.model("Post", postSchema);

// 모든 포스트를 리턴
export async function getAll() {
  return Post.find().sort({ createdAt: -1 });
}

// 사용자 아이디(userid)에 대한 포스트를 리턴
export async function getAllByUserid(userid) {
  return Post.find({ userid }).sort({ createdAt: -1 });
}

// 글 번호(id)에 대한 포스트를 리턴
export async function getById(id) {
  return Post.findById(id);
}

// 포스트를 작성
export async function create(text, id) {
  return UserRepository.findById(id).then((user) =>
    new Post({
      text,
      userIdx: user.id,
      name: user.name,
      userid: user.userid,
      url: user.url,
    }).save()
  );
}

// 포스트를 변경
export async function update(id, text) {
  // 바뀌고 나서의 결과를 리턴
  return Post.findByIdAndUpdate(id, { text }, { returnDocument: "after" });
}

// 포스트를 삭제
export async function remove(id) {
  return Post.findByIdAndDelete(id);
}

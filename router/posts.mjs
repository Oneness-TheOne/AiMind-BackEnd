import express from "express";
import * as postController from "../controller/post.mjs";
import { body } from "express-validator"; // 괄호가 없으면 export default를 가져옴. {필수}
import { validate } from "../middleware/validator.mjs";
import { isAuth } from "../middleware/auth.mjs";

const router = express.Router();

// 에러 나면 validator.ms로 넘김
// 다 끝나면 validate로 가서 결과를 받아온다
// 그게 validPost에 저장됨
const validatePost = [
  body("text").trim().isLength({ min: 4 }).withMessage("최소 4자 이상 입력"),
  validate,
];

// 전체 포스트 가져오기
// 특정 아이디에 대한 포스트 가져오기
// http://127.0.0.1:8080/post
// http://127.0.0.1:8080/post?userid=1
// 콜백으로 함수를 실행하는 것이 아닌 주소 주기
router.get("/", isAuth, postController.getPosts);

// 글번호에 대한 포스트 가져오기
// http://127.0.0.1:8080/post/:id
router.get("/:id", isAuth, postController.getPost);

// 포스트 쓰기
// http://127.0.0.1:8080/post
// validatePost를 거쳐서 통과한 애만 넘어감
router.post("/", isAuth, validatePost, postController.createPost);

// 포스트 수정하기
// http://127.0.0.1:8080/post/:id
router.put("/:id", isAuth, validatePost, postController.updatePost);

// 포스트 삭제하기
// http://127.0.0.1:8080/post/:id
router.delete("/:id", isAuth, postController.deletePost);

export default router;

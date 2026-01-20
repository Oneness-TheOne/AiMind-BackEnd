import { validationResult } from "express-validator"; // 리턴되는지 에러났는지 확인해줌

export const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (errors.isEmpty()) {
    return next(); // 에러 안나면 넘김
  }
  return res.status(400).json({ message: errors.array()[0].msg }); // post의 validatePost의 에러 메세지가 옴
};

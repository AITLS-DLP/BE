# Git Branch Sync Guide

이 문서는 현재 저장소(`work` 브랜치)에 있는 최신 변경 사항을 사용자의 원격 저장소로 푸시하는 방법을 설명합니다. 원하는 목표는 `feature/integration` 브랜치에 반영하는 것이며, 필요하다면 `feature/log` 브랜치로도 업로드할 수 있습니다.

## 1. 원격 저장소 연결 확인
먼저 작업 환경에 사용자의 원격 저장소가 등록되어 있는지 확인합니다.

```bash
git remote -v
```

원격이 등록되어 있지 않다면 다음과 같이 추가합니다.

```bash
git remote add origin <your-repo-url>
```

이미 다른 이름(`origin` 외)에 연결되어 있다면 해당 별칭을 사용해도 무방합니다.

## 2. 최신 변경 사항 확인
현재 브랜치(`work`)에 원하는 커밋이 들어 있는지 다시 한 번 점검합니다.

```bash
git status
git log --oneline --decorate -5
```

출력에 `Connect Admin-FE pages to backend APIs` 커밋 등 필요한 작업이 포함되어 있는지 확인합니다.

## 3. 대상 브랜치 준비
### A. `feature/integration` 브랜치에 푸시하기
1. 원격에 `feature/integration` 브랜치가 없으면 로컬에서 동일한 이름의 브랜치를 만들고 체크아웃합니다.
   ```bash
   git checkout -b feature/integration
   ```
2. 이미 존재하는 브랜치라면 단순히 체크아웃합니다.
   ```bash
   git checkout feature/integration
   ```
3. `work` 브랜치의 변경 사항을 가져옵니다.
   ```bash
   git merge work
   ```
   또는 `work`에서 바로 푸시하려면 다음 단계로 넘어갑니다.

### B. 대신 `feature/log` 브랜치를 사용할 경우
1. 브랜치를 체크아웃합니다.
   ```bash
   git checkout feature/log
   ```
2. 필요에 따라 `work` 브랜치를 병합하거나, `work`에서 직접 푸시합니다.

## 4. 원격 저장소로 푸시
선택한 브랜치에서 다음 명령으로 변경 사항을 업로드합니다.

```bash
git push -u origin feature/integration
```

`feature/log` 브랜치로 푸시하려면 브랜치 이름만 바꾸면 됩니다.

```bash
git push -u origin feature/log
```

이미 추적이 설정되어 있다면 `-u` 옵션은 생략 가능합니다.

## 5. 푸시 후 처리
- 협업 중이라면 원격 저장소에서 Pull Request(PR)를 생성하여 코드 리뷰 및 병합 절차를 진행합니다.
- 이후 로컬에서 다시 `work` 브랜치로 돌아오려면 `git checkout work`를 실행합니다.

## 6. 문제 해결 팁
- 충돌이 발생하면 Git이 안내하는 파일들을 수정하고 `git add <파일>` → `git commit` → `git push` 순으로 해결합니다.
- 인증 오류가 나오면 SSH 키 또는 HTTPS 자격 증명을 다시 확인합니다.
- 원격 브랜치가 강제로 업데이트되어야 한다면 `git push --force-with-lease origin <브랜치>`를 사용하지만, 협업 환경에서는 신중히 사용하세요.

이 과정을 따르면 현재 환경에서 준비된 백엔드/프론트엔드 연동 코드가 사용자의 원격 저장소의 원하는 브랜치에 안전하게 반영됩니다.
